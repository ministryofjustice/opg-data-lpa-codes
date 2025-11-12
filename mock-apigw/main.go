package main

import (
	"bytes"
	"cmp"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/feature/dynamodb/attributevalue"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

const (
	paperKeyPrefix             = "PAPER#"
	activationKeyTable         = "lpa-codes-local"
	paperVerificationCodeTable = "data-lpa-codes-local"
)

func handler(w http.ResponseWriter, r *http.Request) {
	if handleFixtureRequests(w, r) {
		return
	}

	url := fmt.Sprintf("%s/2015-03-31/functions/function/invocations", os.Getenv("LAMBDA_URL"))

	query := map[string]string{}
	for k, v := range r.URL.Query() {
		query[k] = v[0]
	}

	var reqBody bytes.Buffer
	_, _ = io.Copy(&reqBody, r.Body)

	path := r.URL.Path
	if !strings.HasPrefix(path, "/v1") {
		path = "/v1" + path
	}

	body := events.APIGatewayProxyRequest{
		Body:                  reqBody.String(),
		Path:                  path,
		HTTPMethod:            r.Method,
		MultiValueHeaders:     r.Header,
		QueryStringParameters: query,
	}

	encodedBody, _ := json.Marshal(body)

	proxyReq, err := http.NewRequest("POST", url, io.NopCloser(strings.NewReader(string(encodedBody))))
	if err != nil {
		log.Printf("error: couldn't create proxy request")
	}

	client := &http.Client{}
	resp, err := client.Do(proxyReq)

	if err != nil {
		http.Error(w, "error doing lambda request", http.StatusInternalServerError)
		return
	}

	encodedRespBody, _ := io.ReadAll(resp.Body)

	var respBody events.APIGatewayProxyResponse
	_ = json.Unmarshal(encodedRespBody, &respBody)

	if respBody.StatusCode == 0 {
		log.Print(string(encodedRespBody))
		http.Error(w, "error from lambda", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", respBody.Headers["Content-Type"])
	w.WriteHeader(respBody.StatusCode)
	_, err = w.Write([]byte(respBody.Body))

	if err != nil {
		log.Println("error writing response body:", err)
	}
}

func handleFixtureRequests(w http.ResponseWriter, r *http.Request) bool {
	if !strings.HasPrefix(r.URL.Path, "/_") {
		return false
	}

	db, err := setupDatabase(r.Context())
	if err != nil {
		http.Error(w, "error setting up database connection", http.StatusInternalServerError)
		return true
	}

	switch r.URL.Path {
	case "/_reset_database":
		if err := resetDatabase(db, r.Context()); err != nil {
			log.Printf("Error reseting database: %s", err.Error())
			http.Error(w, err.Error(), http.StatusInternalServerError)
		} else {
			w.WriteHeader(200)
		}

		return true
	case "/_pact_state":
		if err := handlePactState(db, r.Context(), r.Body); err != nil {
			log.Printf("Error setting up state: %s", err.Error())
			http.Error(w, err.Error(), http.StatusInternalServerError)
		} else {
			w.WriteHeader(200)
		}

		return true
	default:
		return false
	}
}

func resetDatabase(db *dynamodb.Client, ctx context.Context) error {
	if _, err := db.DeleteTable(ctx, &dynamodb.DeleteTableInput{
		TableName: aws.String(activationKeyTable),
	}); err != nil {
		var exception *types.ResourceNotFoundException
		if !errors.As(err, &exception) {
			return err
		}
	}

	if _, err := db.CreateTable(ctx, &dynamodb.CreateTableInput{
		TableName: aws.String(activationKeyTable),
		AttributeDefinitions: []types.AttributeDefinition{
			{AttributeName: aws.String("code"), AttributeType: types.ScalarAttributeTypeS},
			{AttributeName: aws.String("lpa"), AttributeType: types.ScalarAttributeTypeS},
			{AttributeName: aws.String("actor"), AttributeType: types.ScalarAttributeTypeS},
		},
		KeySchema: []types.KeySchemaElement{
			{AttributeName: aws.String("code"), KeyType: types.KeyTypeHash},
		},
		GlobalSecondaryIndexes: []types.GlobalSecondaryIndex{{
			IndexName: aws.String("key_index"),
			KeySchema: []types.KeySchemaElement{
				{AttributeName: aws.String("lpa"), KeyType: types.KeyTypeHash},
				{AttributeName: aws.String("actor"), KeyType: types.KeyTypeRange},
			},
			Projection: &types.Projection{ProjectionType: types.ProjectionTypeAll},
			ProvisionedThroughput: &types.ProvisionedThroughput{
				ReadCapacityUnits:  aws.Int64(5),
				WriteCapacityUnits: aws.Int64(5),
			},
		}},
		ProvisionedThroughput: &types.ProvisionedThroughput{
			ReadCapacityUnits:  aws.Int64(5),
			WriteCapacityUnits: aws.Int64(5),
		},
	}); err != nil {
		return err
	}

	if _, err := db.DeleteTable(ctx, &dynamodb.DeleteTableInput{
		TableName: aws.String(paperVerificationCodeTable),
	}); err != nil {
		var exception *types.ResourceNotFoundException
		if !errors.As(err, &exception) {
			return err
		}
	}

	if _, err := db.CreateTable(ctx, &dynamodb.CreateTableInput{
		TableName: aws.String(paperVerificationCodeTable),
		AttributeDefinitions: []types.AttributeDefinition{
			{AttributeName: aws.String("PK"), AttributeType: types.ScalarAttributeTypeS},
			{AttributeName: aws.String("ActorLPA"), AttributeType: types.ScalarAttributeTypeS},
		},
		KeySchema: []types.KeySchemaElement{
			{AttributeName: aws.String("PK"), KeyType: types.KeyTypeHash},
		},
		GlobalSecondaryIndexes: []types.GlobalSecondaryIndex{{
			IndexName: aws.String("ActorLPAIndex"),
			KeySchema: []types.KeySchemaElement{
				{AttributeName: aws.String("ActorLPA"), KeyType: types.KeyTypeHash},
				{AttributeName: aws.String("PK"), KeyType: types.KeyTypeRange},
			},
			Projection: &types.Projection{ProjectionType: types.ProjectionTypeAll},
			ProvisionedThroughput: &types.ProvisionedThroughput{
				ReadCapacityUnits:  aws.Int64(5),
				WriteCapacityUnits: aws.Int64(5),
			},
		}},
		ProvisionedThroughput: &types.ProvisionedThroughput{
			ReadCapacityUnits:  aws.Int64(5),
			WriteCapacityUnits: aws.Int64(5),
		},
	}); err != nil {
		return err
	}

	return nil
}

func handlePactState(db *dynamodb.Client, ctx context.Context, body io.ReadCloser) error {
	var state struct {
		State string `json:"state"`
	}

	if err := json.NewDecoder(body).Decode(&state); err != nil {
		return err
	}

	re := regexp.MustCompile(`^the paper verification code (P(-[A-Z0-9]{4}){3}-[A-Z0-9]{2})(.*)$`)
	if matches := re.FindStringSubmatch(state.State); len(matches) > 0 {
		code := matches[1]
		record := matches[3]
		key := codes.Key{
			LPA:   "M-7890-0400-4003",
			Actor: "ce118b6e-d8e1-11e7-9296-cec278b6b50a",
		}
		item := codes.PaperVerificationCode{
			PK:        paperKeyPrefix + code,
			ActorLPA:  key.ToActorLPA(),
			UpdatedAt: time.Now(),
		}

		log.Printf("PACT state found code %s with record '%s'", code, record)

		switch record {
		case " is valid and unused":
		case " has not got an expiry date":
		case " is valid and was used 1 year ago":
			item.ExpiresAt = time.Now().AddDate(-1, 0, 0)
			item.ExpiryReason = codes.ExpiryReasonFirstTimeUse
		case " does not exist":
			key, err := attributevalue.Marshal(paperKeyPrefix + code)
			if err != nil {
				return err
			}

			if _, err := db.DeleteItem(ctx, &dynamodb.DeleteItemInput{
				Key: map[string]types.AttributeValue{
					"PK": key,
				},
				TableName: aws.String(paperVerificationCodeTable),
			}); err != nil {
				return nil
			}
			return nil
		}

		// just blindly overwrite. as fixtures is fixtures
		if err := saveFixture(db, ctx, paperVerificationCodeTable, item); err != nil {
			return err
		}
	}

	re = regexp.MustCompile(`^the activation key ([A-Z0-9]{12}) exists(.*)$`)
	if matches := re.FindStringSubmatch(state.State); len(matches) > 0 {
		code := matches[1]
		differentiator := matches[2]
		item := codes.ActivationCode{
			Active:          true,
			Code:            code,
			DateOfBirth:     "1959-08-10",
			ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
			GeneratedDate:   time.Now().Format(time.RFC3339),
			LastUpdatedDate: time.Now().Format(time.RFC3339),
			StatusDetails:   "Generated",
		}

		switch differentiator {
		case " for an actor with a paper verification code":
			item.Actor = "74673c83-05ba-4886-beb1-daaa36fb7984"
			item.LPA = "M-1234-1234-1234"

			key := codes.Key{
				LPA:   item.LPA,
				Actor: item.Actor,
			}
			pvc := codes.PaperVerificationCode{
				PK:        paperKeyPrefix + "P-9876-9876-9876-98",
				ActorLPA:  key.ToActorLPA(),
				UpdatedAt: time.Now(),
			}

			if err := saveFixture(db, ctx, paperVerificationCodeTable, pvc); err != nil {
				return err
			}
		default:
			item.Actor = "700000000002"
			item.LPA = "700000000001"
		}

		// just blindly overwrite. as fixtures is fixtures
		if err := saveFixture(db, ctx, activationKeyTable, item); err != nil {
			return err
		}
	}

	return nil
}

func setupDatabase(requestContext context.Context) (*dynamodb.Client, error) {
	cfg, err := config.LoadDefaultConfig(requestContext)
	if err != nil {
		return nil, err
	}

	cfg.BaseEndpoint = aws.String(cmp.Or(os.Getenv("LOCAL_URL"), "http://localhost:8000"))
	db := dynamodb.NewFromConfig(cfg)

	return db, nil
}

func saveFixture(db *dynamodb.Client, ctx context.Context, table string, item interface{}) error {
	data, err := attributevalue.MarshalMap(item)
	if err != nil {
		return err
	}

	if _, err := db.PutItem(ctx, &dynamodb.PutItemInput{
		TableName: aws.String(table),
		Item:      data,
	}); err != nil {
		return err
	}

	return nil
}

func main() {
	server := &http.Server{
		Addr:              ":8080",
		Handler:           http.HandlerFunc(handler),
		ReadHeaderTimeout: 10 * time.Second,
	}

	if err := server.ListenAndServe(); err != nil {
		log.Fatal(err)
	}

	log.Println("running on port 8080")
}
