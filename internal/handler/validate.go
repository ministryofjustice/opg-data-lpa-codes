package handler

import (
	"context"
	"encoding/json"
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

	codeDetails, err := codesStore.CodesByCode(ctx, v.Code)
	if err != nil {
		return respondInternalServerError(fmt.Errorf("get codes: %w", err))
	}

	if len(codeDetails) != 1 {
		return respondOK(map[string]any{"actor": nil})
	}

	code := codeDetails[0]

	if !code.Active || code.DateOfBirth != v.DateOfBirth || code.LPA != v.LPA {
		return respondOK(map[string]any{"actor": nil})
	}

	return respondOK(map[string]any{"actor": code.Actor})
}
