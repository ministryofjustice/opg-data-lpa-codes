package handler

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

func Revoke(ctx context.Context, codesStore *codes.ActivationCodeStore, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	var v struct {
		Code string `json:"code"`
	}
	if err := json.Unmarshal([]byte(event.Body), &v); err != nil {
		return respondInternalServerError(err)
	}

	if v.Code == "" {
		return respondBadRequest()
	}

	item, err := codesStore.Code(ctx, v.Code)
	if err != nil && !errors.Is(err, codes.ErrCodeNotFound) {
		return respondInternalServerError(fmt.Errorf("get codes: %w", err))
	}

	updated, err := codesStore.RevokeCode(ctx, v.Code)
	if err != nil {
		return respondInternalServerError(fmt.Errorf("update codes: %w", err))
	}

	if updated > 0 {
		if err := publishActivationKeyUsed(ctx, item); err != nil {
			slog.ErrorContext(ctx, "failed to write activation key used event", slog.String("lpa", item.LPA), slog.String("actor", item.Actor), slog.Any("err", err))
		}
	}

	return respondOK(map[string]any{"codes revoked": updated})
}
