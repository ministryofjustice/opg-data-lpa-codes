package main

import (
	"cmp"
	"context"
	"log/slog"
	"os"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/handler"
)

var (
	cfg        aws.Config
	codesStore *codes.Store
)

func run(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	slog.Info("handling", slog.String("method", event.HTTPMethod), slog.String("path", event.Path))

	switch event.Path {
	case "/v1/healthcheck":
		return handler.Healthcheck(ctx, event)
	case "/v1/create":
		return handler.Create(ctx, codesStore, event)
	case "/v1/exists":
		return handler.Exists(ctx, codesStore, event)
	case "/v1/revoke":
		return handler.Revoke(ctx, codesStore, event)
	case "/v1/validate":
		return handler.Validate(ctx, codesStore, event)
	case "/v1/code":
		return handler.Code(ctx, codesStore, event)
	case "/v1/paper-verification-code", "/v1/paper-verification-code/validate", "/v1/paper-verification-code/expire":
		return handler.TODO(ctx, event)
	}

	return handler.RespondNotFound(event.Path)
}

func main() {
	var (
		ctx         = context.Background()
		localURL    = os.Getenv("LOCAL_URL")
		environment = os.Getenv("ENVIRONMENT")
	)

	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	var err error
	cfg, err = config.LoadDefaultConfig(ctx)
	if err != nil {
		slog.ErrorContext(ctx, "failed to load default config", slog.Any("err", err))
		return
	}

	if environment == "ci" || environment == "local" {
		cfg.BaseEndpoint = aws.String(cmp.Or(localURL, "http://localhost:8000"))
	}

	codesStore = codes.NewStore(dynamodb.NewFromConfig(cfg), "lpa-codes-"+environment)

	lambda.Start(run)
}
