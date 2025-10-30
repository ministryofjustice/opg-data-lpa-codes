package handler

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

func Code(ctx context.Context, codesStore *codes.ActivationCodeStore, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
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
	if err != nil {
		if errors.Is(err, codes.ErrNotFound) {
			return RespondNotFound(event.Path)
		}

		return respondInternalServerError(fmt.Errorf("get codes: %w", err))
	}

	return respondOK([]codes.Item{item})
}
