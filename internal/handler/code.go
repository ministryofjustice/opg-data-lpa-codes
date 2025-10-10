package handler

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

func Code(ctx context.Context, codesStore *codes.Store, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
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

	codeDetails, err := codesStore.CodesByCode(ctx, v.Code)
	if err != nil {
		return respondInternalServerError(fmt.Errorf("get codes: %w", err))
	}

	if len(codeDetails) == 0 {
		return respondNotFound()
	}

	return respondOK(codeDetails)
}
