package handler

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

type paperVerificationCodeResponse struct {
	LPA   string `json:"lpa"`
	Actor string `json:"actor"`
	Code  string `json:"code"`
}

func PaperVerificationCode(ctx context.Context, codesStore *codes.Store, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	var data struct {
		LPA   string `json:"lpa"`
		Actor string `json:"actor"`
	}
	if err := json.Unmarshal([]byte(event.Body), &data); err != nil {
		return respondInternalServerError(err)
	}

	if data.Actor == "" || data.LPA == "" {
		return respondBadRequest()
	}

	key := codes.Key{LPA: data.LPA, Actor: data.Actor}

	// 1. expire all existing codes for LPA/Actor combo
	if _, err := codesStore.SupersedeCodes(ctx, key); err != nil {
		return respondInternalServerError(fmt.Errorf("update codes: %w", err))
	}

	// 2. generate a new code
	generatedCode, err := codesStore.GeneratePaperVerificationCode(ctx)
	if err != nil {
		return respondInternalServerError(fmt.Errorf("generate paper verification code: %w", err))
	}

	// 3. insert new code into database
	newCode, err := codesStore.InsertNewPaperVerificationCode(ctx, key, generatedCode)
	if err != nil {
		return respondInternalServerError(fmt.Errorf("insert new paper verification code: %w", err))
	}

	return respondOK(paperVerificationCodeResponse{
		LPA:   data.LPA,
		Actor: data.Actor,
		Code:  newCode.Code,
	})
}
