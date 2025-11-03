package handler

import (
	"encoding/json"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
)

func RespondNotFound(path string) (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{
		StatusCode: http.StatusNotFound,
		Headers:    map[string]string{"Content-Type": "application/json"},
		Body:       `{"body":{"error":{"code":"Not Found","message":"Not found url https://dev.lpa-codes.api.opg.service.justice.gov.uk` + path + `"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":404}`,
	}, nil
}

func respondNotFound() (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{
		StatusCode: http.StatusNotFound,
	}, nil
}

func respondBadRequest() (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{
		StatusCode: http.StatusBadRequest,
		Body:       `{"body":{"error":{"code":"Bad Request","message":"Bad payload"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":400}`,
	}, nil
}

func respondMethodNotAllowed() (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{
		StatusCode: http.StatusMethodNotAllowed,
		Body:       `{"body":{"error":{"code":"Method Not Allowed","message":"Method not supported"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":405}`,
	}, nil
}

func respondInternalServerError(err error) (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{StatusCode: http.StatusInternalServerError}, err
}

func respondOK(v any) (events.APIGatewayProxyResponse, error) {
	body, _ := json.Marshal(v)
	return events.APIGatewayProxyResponse{StatusCode: http.StatusOK, Body: string(body)}, nil
}
