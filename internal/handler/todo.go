package handler

import (
	"context"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
)

func TODO(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if event.HTTPMethod != http.MethodPost {
		return respondMethodNotAllowed()
	}

	return respondInternalServerError(nil)
}
