package codes

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/feature/dynamodb/attributevalue"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

// A PaperVerificationCodeStore contains PaperVerificationCode type records.
type PaperVerificationCodeStore struct {
	dynamo    *dynamodb.Client
	tableName string
}

func NewPaperVerificationCodeStore(dynamo *dynamodb.Client, tableName string) *PaperVerificationCodeStore {
	return &PaperVerificationCodeStore{dynamo: dynamo, tableName: tableName}
}

// CodesByKey returns all unexpired codes for the given key.
func (s *PaperVerificationCodeStore) CodesByKey(ctx context.Context, key Key) ([]PaperVerificationCode, error) {
	output, err := s.dynamo.Query(ctx, &dynamodb.QueryInput{
		IndexName:              aws.String("ActorLPAIndex"),
		TableName:              aws.String(s.tableName),
		KeyConditionExpression: aws.String("#ActorLPA = :ActorLPA"),
		FilterExpression:       aws.String("#ExpiresAt = :Zero or #ExpiresAt > :Now"),
		ExpressionAttributeValues: map[string]types.AttributeValue{
			":ActorLPA": &types.AttributeValueMemberS{Value: key.ToActorLPA()},
			":Now":      &types.AttributeValueMemberS{Value: time.Now().Format(time.RFC3339Nano)},
			":Zero":     &types.AttributeValueMemberS{Value: time.Time{}.Format(time.RFC3339Nano)},
		},
		ExpressionAttributeNames: map[string]string{
			"#ActorLPA":  "ActorLPA",
			"#ExpiresAt": "ExpiresAt",
		},
	})
	if err != nil {
		return nil, err
	}

	if len(output.Items) == 0 {
		return nil, nil
	}

	var v []PaperVerificationCode
	if err := attributevalue.UnmarshalListOfMaps(output.Items, &v); err != nil {
		return nil, err
	}

	return v, nil
}

// SupersedeCodes updates any codes for the given key so that they will expire
// in 1 month.
func (s *PaperVerificationCodeStore) SupersedeCodes(ctx context.Context, key Key) error {
	entries, err := s.CodesByKey(ctx, key)
	if err != nil {
		return err
	}

	if len(entries) == 0 {
		slog.Info("0 rows to update for LPA/Actor")
		return nil
	}

	var items []types.TransactWriteItem
	now := time.Now()

	for _, entry := range entries {
		expiresAt := now.AddDate(0, 1, 0)

		if entry.ExpiresAt.IsZero() || entry.ExpiresAt.After(expiresAt) {
			items = append(items, types.TransactWriteItem{
				Update: &types.Update{
					TableName: aws.String(s.tableName),
					Key: map[string]types.AttributeValue{
						"PK": &types.AttributeValueMemberS{Value: entry.PK},
					},
					UpdateExpression:    aws.String("SET #ExpiresAt = :ExpiresAt, #UpdatedAt = :UpdatedAt"),
					ConditionExpression: aws.String("#ExpiresAt = :Zero OR #ExpiresAt > :ExpiresAt"),
					ExpressionAttributeValues: map[string]types.AttributeValue{
						":ExpiresAt": &types.AttributeValueMemberS{Value: expiresAt.Format(time.RFC3339Nano)},
						":UpdatedAt": &types.AttributeValueMemberS{Value: now.Format(time.RFC3339Nano)},
						":Zero":      &types.AttributeValueMemberS{Value: time.Time{}.Format(time.RFC3339Nano)},
					},
					ExpressionAttributeNames: map[string]string{
						"#ExpiresAt": "ExpiresAt",
						"#UpdatedAt": "UpdatedAt",
					},
				},
			})
		}
	}

	if len(items) == 0 {
		return nil
	}

	if _, err := s.dynamo.TransactWriteItems(ctx, &dynamodb.TransactWriteItemsInput{
		TransactItems: items,
	}); err != nil {
		return err
	}

	slog.Info(fmt.Sprintf("%d rows updated for LPA/Actor", len(items)))
	return nil
}

// Create a new paper verification code, retrying up to 10 times to get a unique code.
func (s *PaperVerificationCodeStore) Create(ctx context.Context, key Key) (code PaperVerificationCode, err error) {
	for range 10 {
		code, err = s.tryCreate(ctx, key)
		if err != nil {
			var ccfe types.ConditionalCheckFailedException
			if errors.Is(err, &ccfe) {
				continue
			}

			return PaperVerificationCode{}, err
		}

		return code, nil
	}

	return PaperVerificationCode{}, err
}

// tryCreate generates and puts a new code, if it doesn't already exist,
// returning the created PaperVerificationCode.
func (s *PaperVerificationCodeStore) tryCreate(ctx context.Context, key Key) (PaperVerificationCode, error) {
	newCode := randomPaperVerificationCode()

	item := PaperVerificationCode{
		PK:        paperKeyPrefix + newCode,
		ActorLPA:  key.ToActorLPA(),
		UpdatedAt: time.Now(),
	}

	data, err := attributevalue.MarshalMap(item)
	if err != nil {
		return PaperVerificationCode{}, err
	}

	if _, err := s.dynamo.PutItem(ctx, &dynamodb.PutItemInput{
		TableName:           aws.String(s.tableName),
		Item:                data,
		ConditionExpression: aws.String("attribute_not_exists(PK)"),
	}); err != nil {
		return PaperVerificationCode{}, err
	}

	return item, nil
}
