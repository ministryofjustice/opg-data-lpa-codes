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

func Validate(ctx context.Context, codesStore *codes.Store, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	var v struct {
		Code        string `json:"code"`
		LPA         string `json:"lpa"`
		DateOfBirth string `json:"dob"`
	}
	if err := json.Unmarshal([]byte(event.Body), &v); err != nil {
		return respondInternalServerError(err)
	}

	if v.Code == "" || v.LPA == "" || v.DateOfBirth == "" {
		return respondBadRequest()
	}

	item, err := codesStore.Code(ctx, v.Code)
	if err != nil {
		if errors.Is(err, codes.ErrNotFound) {
			return respondOK(map[string]any{"actor": nil})
		}

		return respondInternalServerError(fmt.Errorf("get codes: %w", err))
	}

	if !item.Active || item.DateOfBirth != v.DateOfBirth || item.LPA != v.LPA {
		return respondOK(map[string]any{"actor": nil})
	}

	return respondOK(map[string]any{"actor": item.Actor})
}
