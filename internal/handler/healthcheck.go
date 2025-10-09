package handler

import (
	"context"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
)

func Healthcheck(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	switch event.HTTPMethod {
	case http.MethodGet:
		return events.APIGatewayProxyResponse{
			StatusCode: http.StatusOK,
			Headers:    map[string]string{"Content-Length": "5", "Content-Type": "application/json"},
			Body: `"OK"
`,
		}, nil

	case http.MethodHead:
		return events.APIGatewayProxyResponse{
			StatusCode: http.StatusOK,
			Headers:    map[string]string{"Content-Length": "5", "Content-Type": "application/json"},
			Body:       ``,
		}, nil
	}

	return respondMethodNotAllowed()
}
