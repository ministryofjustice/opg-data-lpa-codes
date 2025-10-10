package handler

import (
	"encoding/json"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
)

func respondBadRequest() (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{StatusCode: http.StatusBadRequest, Body: `{
	"body": {"error":{"code":"Bad Request","message":"Bad payload"}},
	"headers": {"Content-Type": "application/json"},
	"isBase64Encoded": false,
	"statusCode": 400
}`}, nil
}

func respondMethodNotAllowed() (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{StatusCode: http.StatusMethodNotAllowed}, nil
}

func respondNotFound() (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{StatusCode: http.StatusNotFound}, nil
}

func respondInternalServerError(err error) (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{StatusCode: http.StatusMethodNotAllowed}, err
}

func respondOK(v any) (events.APIGatewayProxyResponse, error) {
	body, _ := json.Marshal(v)
	return events.APIGatewayProxyResponse{StatusCode: http.StatusOK, Body: string(body)}, nil
}
