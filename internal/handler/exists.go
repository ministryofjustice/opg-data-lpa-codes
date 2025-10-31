package handler

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

func Exists(ctx context.Context, codesStore *codes.ActivationCodeStore, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	var v struct {
		LPA   string `json:"lpa"`
		Actor string `json:"actor"`
	}
	if err := json.Unmarshal([]byte(event.Body), &v); err != nil {
		return respondInternalServerError(err)
	}

	if v.LPA == "" || v.Actor == "" {
		return respondBadRequest()
	}

	key := codes.Key{LPA: v.LPA, Actor: v.Actor}

	codeDetails, err := codesStore.CodesByKey(ctx, key)
	if err != nil {
		return respondInternalServerError(fmt.Errorf("get codes: %w", err))
	}

	for _, code := range codeDetails {
		if code.Active {
			return respondOK(map[string]string{"Created": code.GeneratedDate})
		}
	}

	return respondOK(map[string]any{"Created": nil})
}
