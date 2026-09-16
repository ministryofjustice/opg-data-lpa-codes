package main

import (
	"cmp"
	"context"
	"fmt"
	"log/slog"
	"os"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/eventbridge"
	"github.com/aws/aws-sdk-go-v2/service/eventbridge/types"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/handler"
)

var (
	cfg                        aws.Config
	activationCodeStore        *codes.ActivationCodeStore
	paperVerificationCodeStore *codes.PaperVerificationCodeStore
)

func run(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	slog.Info("handling", slog.String("method", event.HTTPMethod), slog.String("path", event.Path))

	switch event.Path {
	case "/v1/healthcheck":
		return handler.Healthcheck(ctx, event)
	case "/v1/create":
		return handler.Create(ctx, activationCodeStore, event)
	case "/v1/exists":
		return handler.Exists(ctx, activationCodeStore, event)
	case "/v1/revoke":
		return handler.Revoke(ctx, activationCodeStore, event)
	case "/v1/validate":
		return handler.Validate(ctx, activationCodeStore, paperVerificationCodeStore, event)
	case "/v1/code":
		return handler.Code(ctx, activationCodeStore, event)
	case "/v1/paper-verification-code":
		return handler.PaperVerificationCode(ctx, paperVerificationCodeStore, event)
	case "/v1/paper-verification-code/validate":
		return handler.ValidatePaperVerificationCode(ctx, paperVerificationCodeStore, event)
	case "/v1/paper-verification-code/expire":
		return handler.ExpirePaperVerificationCode(ctx, paperVerificationCodeStore, event)
	}

	return handler.RespondNotFound(event.Path)
}

func parseSlogLevel(s string) slog.Level {
	var level slog.Level
	if err := level.UnmarshalText([]byte(s)); err != nil {
		return slog.LevelInfo
	}

	return level
}

func main() {
	var (
		ctx         = context.Background()
		loggerLevel = parseSlogLevel(os.Getenv("LOGGER_LEVEL"))
		localURL    = os.Getenv("LOCAL_URL")
		environment = os.Getenv("ENVIRONMENT")
	)

	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: loggerLevel}))
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

	activationCodeStore = codes.NewActivationCodeStore(dynamodb.NewFromConfig(cfg), "lpa-codes-"+environment)
	paperVerificationCodeStore = codes.NewPaperVerificationCodeStore(dynamodb.NewFromConfig(cfg), "data-lpa-codes-"+environment)

	handler.SetActivationKeyUsedPublisher(func(ctx context.Context, item codes.ActivationCode) error {
		busName := os.Getenv("OUTBOUND_EVENT_BUS")
		if busName == "" {
			slog.WarnContext(ctx, "OUTBOUND_EVENT_BUS is not set; skipping activation key used event")
			return nil
		}

		detail, err := handler.MarshalActivationKeyUsedEvent(item)
		if err != nil {
			return fmt.Errorf("marshal activation key used event: %w", err)
		}

		response, err := eventbridge.NewFromConfig(cfg).PutEvents(ctx, &eventbridge.PutEventsInput{
			Entries: []types.PutEventsRequestEntry{{
				Source:       aws.String("opg.poas.use"),
				DetailType:   aws.String("activation-key-used"),
				Detail:       aws.String(string(detail)),
				EventBusName: aws.String(busName),
			}},
		})
		if err != nil {
			return fmt.Errorf("put activation key used event: %w", err)
		}
		if response.FailedEntryCount > 0 {
			for _, entry := range response.Entries {
				if entry.ErrorCode != nil || entry.ErrorMessage != nil {
					return handler.EventBridgeError(entry.ErrorCode, entry.ErrorMessage)
				}
			}
		}
		return nil
	})

	lambda.Start(run)
}
