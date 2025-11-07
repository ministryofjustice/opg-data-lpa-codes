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

const paperKeyPrefix = "PAPER#"

func handler(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path == "/_reset_database" {
		if err := resetDatabase(r.Context()); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}

		return
	}

	if r.URL.Path == "/_pact_state" {
		if err := handlePactState(r); err != nil {
			log.Printf("Error setting up state: %s", err.Error())
			http.Error(w, err.Error(), http.StatusInternalServerError)
		} else {
			w.WriteHeader(200)
		}

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

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(respBody.StatusCode)
	_, err = w.Write([]byte(respBody.Body))

	if err != nil {
		log.Println("error writing response body:", err)
	}
}

func resetDatabase(ctx context.Context) error {
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return err
	}

	cfg.BaseEndpoint = aws.String(cmp.Or(os.Getenv("LOCAL_URL"), "http://localhost:8000"))

	db := dynamodb.NewFromConfig(cfg)

	if _, err := db.DeleteTable(ctx, &dynamodb.DeleteTableInput{
		TableName: aws.String("lpa-codes-local"),
	}); err != nil {
		var exception *types.ResourceNotFoundException
		if !errors.As(err, &exception) {
			return err
		}
	}

	if _, err := db.CreateTable(ctx, &dynamodb.CreateTableInput{
		TableName: aws.String("lpa-codes-local"),
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
		TableName: aws.String("data-lpa-codes-local"),
	}); err != nil {
		var exception *types.ResourceNotFoundException
		if !errors.As(err, &exception) {
			return err
		}
	}

	if _, err := db.CreateTable(ctx, &dynamodb.CreateTableInput{
		TableName: aws.String("data-lpa-codes-local"),
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

func handlePactState(r *http.Request) error {
	var state struct {
		State string `json:"state"`
	}

	if err := json.NewDecoder(r.Body).Decode(&state); err != nil {
		return err
	}

	cfg, err := config.LoadDefaultConfig(r.Context())
	if err != nil {
		return err
	}

	cfg.BaseEndpoint = aws.String(cmp.Or(os.Getenv("LOCAL_URL"), "http://localhost:8000"))
	db := dynamodb.NewFromConfig(cfg)

	re := regexp.MustCompile(`^the paper verification code (P(-[A-Z0-9]{4}){3}-[A-Z0-9]{2}) (.*)$`)
	if matches := re.FindStringSubmatch(state.State); len(matches) > 0 {
		code := matches[1]
		record := matches[3]
		key := codes.Key{
			LPA:   "M-7890-0400-4003",
			Actor: "ce118b6e-d8e1-11e7-9296-cec278b6b50a",
		}

		log.Printf("PACT state found code %s with record '%s'", code, record)

		var item codes.PaperVerificationCode
		switch record {
		case "is valid and unused":
		case "has not got an expiry date":
			item = codes.PaperVerificationCode{
				PK:        paperKeyPrefix + code,
				ActorLPA:  key.ToActorLPA(),
				UpdatedAt: time.Now(),
			}
			break
		case "is valid and was used 1 year ago":
			item = codes.PaperVerificationCode{
				PK:           paperKeyPrefix + code,
				ActorLPA:     key.ToActorLPA(),
				UpdatedAt:    time.Now(),
				ExpiresAt:    time.Now().AddDate(-1, 0, 0),
				ExpiryReason: codes.ExpiryReasonFirstTimeUse,
			}
			break
		case "does not exist":
			break
		}

		if item.PK == "" {
			return nil
		}

		data, err := attributevalue.MarshalMap(item)
		if err != nil {
			return err
		}

		// just blindly overwrite. as fixtures is fixtures
		if _, err := db.PutItem(r.Context(), &dynamodb.PutItemInput{
			TableName: aws.String("data-lpa-codes-local"),
			Item:      data,
		}); err != nil {
			return err
		}
	}

	re = regexp.MustCompile(`^the activation key ([A-Z0-9]{12}) exists$`)
	if matches := re.FindStringSubmatch(state.State); len(matches) > 0 {
		code := matches[1]

		item := codes.ActivationCode{
			Active:          true,
			Actor:           "700000000002",
			Code:            code,
			DateOfBirth:     "1959-08-10",
			ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
			GeneratedDate:   time.Now().Format(time.RFC3339),
			LastUpdatedDate: time.Now().Format(time.RFC3339),
			LPA:             "700000000001",
			StatusDetails:   "Generated",
		}

		data, err := attributevalue.MarshalMap(item)
		if err != nil {
			return err
		}

		// just blindly overwrite. as fixtures is fixtures
		if _, err := db.PutItem(r.Context(), &dynamodb.PutItemInput{
			TableName: aws.String("lpa-codes-local"),
			Item:      data,
		}); err != nil {
			return err
		}
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
