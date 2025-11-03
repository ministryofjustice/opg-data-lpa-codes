package handler

import (
	"context"
	"encoding/json"
	"net/http"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

type expirePaperVerificationCodeResponse struct {
	ExpiryDate string `json:"expiry_date"`
}

func ExpirePaperVerificationCode(ctx context.Context, codesStore *codes.PaperVerificationCodeStore, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	var data struct {
		Code         string             `json:"code"`
		ExpiryReason codes.ExpiryReason `json:"expiry_reason"`
	}
	if err := json.Unmarshal([]byte(event.Body), &data); err != nil {
		return respondInternalServerError(err)
	}

	if data.Code == "" || data.ExpiryReason == codes.ExpiryReasonUnset {
		return respondBadRequest()
	}

	expiresAt, err := codesStore.SetExpiry(ctx, data.Code, data.ExpiryReason)
	if err != nil {
		return respondInternalServerError(err)
	}

	return respondOK(expirePaperVerificationCodeResponse{
		ExpiryDate: expiresAt.Format(time.DateOnly),
	})
}
