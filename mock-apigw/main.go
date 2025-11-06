package main

import (
	"bytes"
	"cmp"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"iter"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

func handler(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path == "/reset-database" {
		if err := resetDatabase(r.Context()); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
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

	body := events.APIGatewayProxyRequest{
		Body:                  reqBody.String(),
		Path:                  r.URL.Path,
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

	for _, tableName := range []string{"lpa-codes-local", "data-lpa-codes-local"} {
		for final := range ticker() {
			var (
				notFound *types.ResourceNotFoundException
				inUse    *types.ResourceInUseException
			)

			if _, err := db.DeleteTable(ctx, &dynamodb.DeleteTableInput{
				TableName: aws.String(tableName),
			}); err != nil {
				if errors.As(err, &inUse) && !final {
					continue
				} else if !errors.As(err, &notFound) {
					return fmt.Errorf("deleting %s: %w", tableName, err)
				}

				break
			}
		}
	}

	for final := range ticker() {
		output, err := db.ListTables(ctx, &dynamodb.ListTablesInput{})
		if err != nil {
			return fmt.Errorf("checking deleted: %w", err)
		}

		if len(output.TableNames) == 0 {
			break
		}

		if final {
			return fmt.Errorf("tables not deleted, still have %d", len(output.TableNames))
		}
	}

	for final := range ticker() {
		_, lpaCodesLocalError := db.CreateTable(ctx, &dynamodb.CreateTableInput{
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
		})

		_, dataLpaCodesLocalError := db.CreateTable(ctx, &dynamodb.CreateTableInput{
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
		})

		output, err := db.ListTables(ctx, &dynamodb.ListTablesInput{})
		if err != nil {
			return fmt.Errorf("checking created: %w", err)
		}

		if len(output.TableNames) == 2 {
			break
		}

		if final {
			return fmt.Errorf(`tables not created, only have %v:
lpa-codes-local: %s
data-lpa-codes-local: %s`, output.TableNames, lpaCodesLocalError, dataLpaCodesLocalError)
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

// ticker waits an increasing amount between each iteraction and yields true
// on the final iteration.
func ticker() iter.Seq[bool] {
	const (
		max = 10
		dur = 100 * time.Millisecond
	)

	return func(yield func(bool) bool) {
		for i := range max {
			if !yield(i == max-1) {
				return
			}

			time.Sleep(dur * time.Duration(i))
		}
	}
}
