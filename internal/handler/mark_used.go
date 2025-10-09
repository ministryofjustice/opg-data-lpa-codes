package handler

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

func MarkUsed(ctx context.Context, codesStore *codes.Store, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
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

	updated, err := codesStore.SetExpiryForCode(ctx, v.Code, time.Now().AddDate(2, 0, 0))
	if err != nil {
		return respondInternalServerError(fmt.Errorf("update codes: %w", err))
	}

	return respondOK(map[string]any{"codes marked used": updated})
}
