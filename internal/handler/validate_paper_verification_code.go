package handler

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

type validatePaperVerificationCodeResponse struct {
	LPA          string `json:"lpa"`
	Actor        string `json:"actor"`
	ExpiryDate   string `json:"expiry_date,omitempty"`
	ExpiryReason string `json:"expiry_reason,omitempty"`
}

func ValidatePaperVerificationCode(ctx context.Context, codesStore *codes.PaperVerificationCodeStore, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	var data struct {
		Code string `json:"code"`
	}
	if err := json.Unmarshal([]byte(event.Body), &data); err != nil {
		return respondInternalServerError(err)
	}

	if data.Code == "" {
		return respondBadRequest()
	}

	code, err := codesStore.Code(ctx, data.Code)
	if err != nil {
		if errors.Is(err, codes.ErrNotFound) {
			return respondOK(struct{}{})
		}

		return respondInternalServerError(err)
	}

	response := validatePaperVerificationCodeResponse{
		LPA:          code.LPA(),
		Actor:        code.Actor(),
		ExpiryReason: code.ExpiryReason,
	}

	if !code.ExpiresAt.IsZero() {
		response.ExpiryDate = code.ExpiresAt.Format(time.DateOnly)
	}

	return respondOK(response)
}
