package handler

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strings"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

type validateRequest struct {
	Code        string `json:"code"`
	LPA         string `json:"lpa"`
	DateOfBirth string `json:"dob"`
}

type validateResponse struct {
	Actor                    *string `json:"actor"`
	HasPaperVerificationCode bool    `json:"has_paper_verification_code,omitempty"`
}

func Validate(ctx context.Context, codesStore *codes.ActivationCodeStore, paperStore *codes.PaperVerificationCodeStore, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	var v validateRequest
	if err := json.Unmarshal([]byte(event.Body), &v); err != nil {
		return respondInternalServerError(err)
	}

	if v.Code == "" || v.LPA == "" || v.DateOfBirth == "" {
		return respondBadRequest()
	}

	item, err := codesStore.Code(ctx, v.Code)
	if err != nil {
		if errors.Is(err, codes.ErrCodeNotFound) {
			return respondOK(validateResponse{})
		}

		return respondInternalServerError(fmt.Errorf("get codes: %w", err))
	}

	if !item.Active || item.DateOfBirth != v.DateOfBirth || item.LPA != v.LPA {
		return respondOK(validateResponse{})
	}

	response := validateResponse{Actor: &item.Actor}

	if strings.HasPrefix(item.LPA, "M-") {
		codes, err := paperStore.CodesByKey(ctx, codes.Key{Actor: item.Actor, LPA: item.LPA})
		if err != nil {
			return respondInternalServerError(fmt.Errorf("checking for paper codes: %w", err))
		}

		if len(codes) > 0 {
			response.HasPaperVerificationCode = true
		}
	}

	return respondOK(response)
}
