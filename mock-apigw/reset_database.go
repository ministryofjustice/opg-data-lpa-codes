package main

import (
	"cmp"
	"context"
	"errors"
	"fmt"
	"iter"
	"os"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

func resetDatabase(ctx context.Context) error {
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return err
	}

	cfg.BaseEndpoint = aws.String(cmp.Or(os.Getenv("LOCAL_URL"), "http://localhost:8000"))

	db := dynamodb.NewFromConfig(cfg)

	output, err := db.ListTables(ctx, &dynamodb.ListTablesInput{})
	if err != nil {
		return fmt.Errorf("checking created: %w", err)
	}

	if len(output.TableNames) != 2 {
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
			var inUse *types.ResourceInUseException
			if !errors.As(err, &inUse) {
				return fmt.Errorf("creating lpa-codes-local: %w", err)
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
			var inUse *types.ResourceInUseException
			if !errors.As(err, &inUse) {
				return fmt.Errorf("creating data-lpa-codes-local: %w", err)
			}
		}
	}

	for final := range ticker() {
		output, err := db.ListTables(ctx, &dynamodb.ListTablesInput{})
		if err != nil {
			return fmt.Errorf("checking created: %w", err)
		}

		if len(output.TableNames) == 2 {
			break
		}

		if final {
			return fmt.Errorf("tables not created, have: %v", output.TableNames)
		}
	}

	if err := deleteItems(ctx, db, "lpa-codes-local", "code"); err != nil {
		return err
	}

	if err := deleteItems(ctx, db, "data-lpa-codes-local", "PK"); err != nil {
		return err
	}

	return nil
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

func deleteItems(ctx context.Context, db *dynamodb.Client, tableName, key string) error {
	for {
		output, err := db.Scan(ctx, &dynamodb.ScanInput{
			TableName:            aws.String(tableName),
			ProjectionExpression: aws.String(key),
			ConsistentRead:       aws.Bool(true),
		})
		if err != nil {
			return fmt.Errorf("scan %s: %w", tableName, err)
		}

		if output.Count == 0 {
			break
		}

		wr := make([]types.WriteRequest, output.Count)
		for i, item := range output.Items {
			wr[i] = types.WriteRequest{
				DeleteRequest: &types.DeleteRequest{
					Key: map[string]types.AttributeValue{
						key: item[key],
					},
				},
			}
		}

		if _, err := db.BatchWriteItem(ctx, &dynamodb.BatchWriteItemInput{
			RequestItems: map[string][]types.WriteRequest{
				tableName: wr,
			},
		}); err != nil {
			return fmt.Errorf("batch write item %s: %w", tableName, err)
		}
	}

	return nil
}
