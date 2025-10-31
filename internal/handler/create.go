package handler

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

type createResponse struct {
	Codes []createResponseItem `json:"codes"`
}

type createResponseItem struct {
	LPA   string `json:"lpa"`
	Actor string `json:"actor"`
	Code  string `json:"code"`
}

func Create(ctx context.Context, codesStore *codes.ActivationCodeStore, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	var data struct {
		LPAs []struct {
			LPA         string `json:"lpa"`
			Actor       string `json:"actor"`
			DateOfBirth string `json:"dob"`
		} `json:"lpas"`
	}
	if err := json.Unmarshal([]byte(event.Body), &data); err != nil {
		return respondInternalServerError(err)
	}

	for _, entry := range data.LPAs {
		if entry.Actor == "" || entry.DateOfBirth == "" || entry.LPA == "" {
			return respondBadRequest()
		}
	}

	response := createResponse{}
	for _, entry := range data.LPAs {
		key := codes.Key{LPA: entry.LPA, Actor: entry.Actor}

		// 1. expire all existing codes for LPA/Actor combo
		if _, err := codesStore.SupersedeCodes(ctx, key); err != nil {
			return respondInternalServerError(fmt.Errorf("update codes: %w", err))
		}

		// 2. generate a new code
		generatedCode, err := codesStore.GenerateCode(ctx)
		if err != nil {
			return respondInternalServerError(fmt.Errorf("generate code: %w", err))
		}

		// 3. insert new code into database
		newCode, err := codesStore.InsertNewCode(ctx, key, entry.DateOfBirth, generatedCode)
		if err != nil {
			return respondInternalServerError(fmt.Errorf("insert new code: %w", err))
		}

		response.Codes = append(response.Codes, createResponseItem{
			LPA:   entry.LPA,
			Actor: entry.Actor,
			Code:  newCode.Code,
		})
	}

	return respondOK(response)
}
