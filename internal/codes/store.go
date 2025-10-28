package codes

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"maps"
	"slices"
	"strconv"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/feature/dynamodb/attributevalue"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

var ErrNotFound = errors.New("code not found")

type Key struct {
	LPA   string
	Actor string
}

type Item struct {
	Active          bool   `json:"active" dynamodbav:"active"`
	Actor           string `json:"actor" dynamodbav:"actor"`
	Code            string `json:"code" dynamodbav:"code"`
	DateOfBirth     string `json:"dob" dynamodbav:"dob"`
	ExpiryDate      int64  `json:"expiry_date" dynamodbav:"expiry_date"`
	GeneratedDate   string `json:"generated_date" dynamodbav:"generated_date"`
	LastUpdatedDate string `json:"last_updated_date" dynamodbav:"last_updated_date"`
	LPA             string `json:"lpa" dynamodbav:"lpa"`
	StatusDetails   status `json:"status_details" dynamodbav:"status_details"`
}

type Store struct {
	dynamo    *dynamodb.Client
	tableName string
}

func NewStore(dynamo *dynamodb.Client, tableName string) *Store {
	return &Store{dynamo: dynamo, tableName: tableName}
}

// GenerateCode returns a 12-digit alphanumeric code containing no ambiguous
// characters. It should be unique at the time of generating, we try 10 times
// and error if a unique code cannot be generated.
func (s *Store) GenerateCode(ctx context.Context) (string, error) {
	for range 10 {
		newCode := randomActivationCode()

		_, err := s.Code(ctx, newCode)
		if err != nil {
			if errors.Is(err, ErrNotFound) {
				return newCode, nil
			}

			return "", err
		}
	}

	slog.Error("Unable to generate unique code - failed after 10 attempts")
	return "", errors.New("generate code reached max attempts")
}

// GeneratePaperVerificationCode returns a formatted alphanumeric code
// containing no ambiguous characters. It should be unique at the time of
// generating, we try 10 times and error if a unique code cannot be generated.
func (s *Store) GeneratePaperVerificationCode(ctx context.Context) (string, error) {
	for range 10 {
		newCode := randomPaperVerificationCode()

		_, err := s.Code(ctx, newCode)
		if err != nil {
			if errors.Is(err, ErrNotFound) {
				return newCode, nil
			}

			return "", err
		}
	}

	return "", errors.New("generate paper verification code reached max attempts")
}

// Code gets the details for the given code, checking that it is not expired. If
// the code does not exist or is expired an ErrNotFound error is returned.
func (s *Store) Code(ctx context.Context, code string) (Item, error) {
	output, err := s.dynamo.GetItem(ctx, &dynamodb.GetItemInput{
		Key: map[string]types.AttributeValue{
			"code": &types.AttributeValueMemberS{Value: code},
		},
		TableName: aws.String(s.tableName),
	})
	if err != nil {
		return Item{}, err
	}

	if output.Item == nil {
		slog.Info("Code does not exist in database")
		return Item{}, ErrNotFound
	}

	var v Item
	if err := attributevalue.UnmarshalMap(output.Item, &v); err != nil {
		return Item{}, err
	}

	if v.ExpiryDate > 0 {
		ttlCutoff := time.Now().Truncate(24 * time.Hour).Unix()
		expiryDate := int64(v.ExpiryDate)

		if expiryDate <= ttlCutoff {
			slog.Info("Code does not exist in database")
			return Item{}, ErrNotFound
		}
	}

	return v, nil
}

// CodesByKey returns all codes for the given key, checking that the code is not
// yet expired.
func (s *Store) CodesByKey(ctx context.Context, key Key) ([]Item, error) {
	ttlCutoff := time.Now().Truncate(24 * time.Hour).Unix()

	output, err := s.dynamo.Query(ctx, &dynamodb.QueryInput{
		IndexName:              aws.String("key_index"),
		TableName:              aws.String(s.tableName),
		KeyConditionExpression: aws.String("#lpa = :lpa and #actor = :actor"),
		FilterExpression:       aws.String("#expiry_date > :ttl_cutoff"),
		ExpressionAttributeValues: map[string]types.AttributeValue{
			":lpa":        &types.AttributeValueMemberS{Value: key.LPA},
			":actor":      &types.AttributeValueMemberS{Value: key.Actor},
			":ttl_cutoff": &types.AttributeValueMemberN{Value: strconv.FormatInt(ttlCutoff, 10)},
		},
		ExpressionAttributeNames: map[string]string{
			"#lpa":         "lpa",
			"#actor":       "actor",
			"#expiry_date": "expiry_date",
		},
	})
	if err != nil {
		return nil, err
	}

	if len(output.Items) == 0 {
		slog.Info("Code does not exist in database")
		return nil, nil
	}

	var v []Item
	if err := attributevalue.UnmarshalListOfMaps(output.Items, &v); err != nil {
		return nil, err
	}

	return v, nil
}

// SupersedeActivationCodes updates the codes for the given key with the status
// details, and makes the codes inactive.
func (s *Store) SupersedeActivationCodes(ctx context.Context, key Key) (int, error) {
	entries, err := s.CodesByKey(ctx, key)
	if err != nil {
		return 0, err
	}

	var toUpdate []Item
	for _, entry := range entries {
		if len(entry.Code) == activationCodeSize {
			toUpdate = append(toUpdate, entry)
		}
	}

	if len(entries) == 0 {
		slog.Info("0 rows updated for LPA/Actor")
		return 0, nil
	}

	updated, err := s.updateEntries(ctx, toUpdate, map[string]any{
		"active":         false,
		"status_details": statusSuperseded,
	})

	slog.Info(fmt.Sprintf("%d rows updated for LPA/Actor", updated))
	return updated, nil
}

// SupersedePaperVerificationCodes updates the codes for the given key with the status
// details, and makes the codes inactive.
func (s *Store) SupersedePaperVerificationCodes(ctx context.Context, key Key) (int, error) {
	entries, err := s.CodesByKey(ctx, key)
	if err != nil {
		return 0, err
	}

	var toUpdate []Item
	for _, entry := range entries {
		if len(entry.Code) == paperVerificationCodeSize {
			toUpdate = append(toUpdate, entry)
		}
	}

	if len(entries) == 0 {
		slog.Info("0 rows updated for LPA/Actor")
		return 0, nil
	}

	updated, err := s.updateEntries(ctx, toUpdate, map[string]any{
		"active":         false,
		"status_details": statusSuperseded,
	})

	slog.Info(fmt.Sprintf("%d rows updated for LPA/Actor", updated))
	return updated, nil
}

// RevokeCode makes the code inactive and sets its status to revoked.
func (s *Store) RevokeCode(ctx context.Context, code string) (int, error) {
	item, err := s.Code(ctx, code)
	if err != nil {
		if errors.Is(err, ErrNotFound) {
			slog.Info("0 rows updated for LPA/Actor")
			return 0, nil
		}

		return 0, err
	}

	updated, err := s.updateEntries(ctx, []Item{item}, map[string]any{
		"active":         false,
		"status_details": statusRevoked,
	})

	slog.Info(fmt.Sprintf("%d rows updated for LPA/Actor", updated))
	return updated, nil
}

// InsertNewCode puts a new code and returns the created Item, once it is inserted.
func (s *Store) InsertNewCode(ctx context.Context, key Key, dateOfBirth, code string) (Item, error) {
	item := Item{
		LPA:             key.LPA,
		Actor:           key.Actor,
		Code:            code,
		Active:          true,
		LastUpdatedDate: time.Now().Format(time.DateOnly),
		DateOfBirth:     dateOfBirth,
		GeneratedDate:   time.Now().Format(time.DateOnly),
		ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
		StatusDetails:   statusGenerated,
	}

	data, err := attributevalue.MarshalMap(item)
	if err != nil {
		return Item{}, err
	}

	if _, err = s.dynamo.PutItem(ctx, &dynamodb.PutItemInput{
		TableName: aws.String(s.tableName),
		Item:      data,
	}); err != nil {
		return Item{}, err
	}

	return item, nil
}

// InsertNewPaperVerificationCode puts a new code and returns the created Item, once it is inserted.
func (s *Store) InsertNewPaperVerificationCode(ctx context.Context, key Key, code string) (Item, error) {
	item := Item{
		LPA:             key.LPA,
		Actor:           key.Actor,
		Code:            code,
		Active:          true,
		LastUpdatedDate: time.Now().Format(time.DateOnly),
		GeneratedDate:   time.Now().Format(time.DateOnly),
		// set expiry into the far future so that we can continue to use this field
		// when querying
		ExpiryDate:    int64(1<<63 - 1),
		StatusDetails: statusGenerated,
	}

	data, err := attributevalue.MarshalMap(item)
	if err != nil {
		return Item{}, err
	}

	if _, err = s.dynamo.PutItem(ctx, &dynamodb.PutItemInput{
		TableName: aws.String(s.tableName),
		Item:      data,
	}); err != nil {
		return Item{}, err
	}

	return item, nil
}

func (s *Store) updateEntries(ctx context.Context, entries []Item, fields map[string]any) (int, error) {
	var (
		attributeNames  = map[string]string{}
		attributeValues = map[string]types.AttributeValue{}
		expression      = []string{}
	)

	fields["last_update_date"] = time.Now().Format(time.DateOnly)

	for i, k := range slices.Sorted(maps.Keys(fields)) {
		attributeNames[fmt.Sprintf("#Field%d", i)] = k
		attributeValues[fmt.Sprintf(":Value%d", i)], _ = attributevalue.Marshal(fields[k])
		expression = append(expression, fmt.Sprintf("#Field%d = :Value%d", i, i))
	}

	var items []types.TransactWriteItem

	for _, entry := range entries {
		if entry.Active {
			items = append(items, types.TransactWriteItem{
				Update: &types.Update{
					TableName: aws.String(s.tableName),
					Key: map[string]types.AttributeValue{
						"code": &types.AttributeValueMemberS{Value: entry.Code},
					},
					UpdateExpression:          aws.String("SET " + strings.Join(expression, ", ")),
					ExpressionAttributeValues: attributeValues,
					ExpressionAttributeNames:  attributeNames,
				},
			})
		}
	}

	_, err := s.dynamo.TransactWriteItems(ctx, &dynamodb.TransactWriteItemsInput{
		TransactItems: items,
	})
	if err != nil {
		return 0, err
	}

	return len(items), nil
}
