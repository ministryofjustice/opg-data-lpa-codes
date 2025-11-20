package handler

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

type expirePaperVerificationCodeRequest struct {
	Code         string             `json:"code"`
	LPA          string             `json:"lpa"`
	Actor        string             `json:"actor"`
	ExpiryReason codes.ExpiryReason `json:"expiry_reason"`
}

type expirePaperVerificationCodeResponse struct {
	ExpiryDate string `json:"expiry_date"`
}

func ExpirePaperVerificationCode(ctx context.Context, codesStore *codes.PaperVerificationCodeStore, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	var data expirePaperVerificationCodeRequest
	if err := json.Unmarshal([]byte(event.Body), &data); err != nil {
		return respondInternalServerError(err)
	}

	// either a code is provided or a lpa/actor pair - and always a reason
	if (data.Code == "" && (data.LPA == "" || data.Actor == "")) || data.ExpiryReason == codes.ExpiryReasonUnset {
		return respondBadRequest()
	}

	// code not provided so lets find one
	if data.Code == "" {
		pvcs, err := codesStore.CodesByKey(ctx, codes.Key{LPA: data.LPA, Actor: data.Actor})
		if err != nil {
			return respondInternalServerError(err)
		}

		if len(pvcs) != 1 {
			return respondCodeNotFound()
		}

		data.Code = pvcs[0].Code()
	}

	expiresAt, err := codesStore.SetExpiry(ctx, data.Code, data.ExpiryReason)
	if err != nil {
		fmt.Printf("%+v\n", err)
		if errors.Is(err, codes.ErrPaperVerificationCodeNotFound) {
			return respondCodeNotFound()
		}

		return respondInternalServerError(err)
	}

	return respondOK(expirePaperVerificationCodeResponse{
		ExpiryDate: expiresAt.Format(time.DateOnly),
	})
}
