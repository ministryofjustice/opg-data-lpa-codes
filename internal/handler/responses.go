package handler

import (
	"encoding/json"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
)

func RespondNotFound(path string) (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{
		StatusCode: http.StatusNotFound,
		Headers:    map[string]string{"Content-Type": "application/vnd.opg-data.v1+json"},
		Body:       `{"errors":[{"code":"OPGDATA-API-NOTFOUND","title":"Not found","detail":"Not found url https://dev.lpa-codes.api.opg.service.justice.gov.uk` + path + `"}]}`,
	}, nil
}

func respondCodeNotFound() (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{
		StatusCode: http.StatusNotFound,
		Headers:    map[string]string{"Content-Type": "application/vnd.opg-data.v1+json"},
		Body:       `{"errors":[{"code":"OPGDATA-API-NOTFOUND","title":"Code not found"}]}`,
	}, nil
}

func respondBadRequest() (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{
		StatusCode: http.StatusBadRequest,
		Headers:    map[string]string{"Content-Type": "application/vnd.opg-data.v1+json"},
		Body:       `{"errors":[{"code":"OPGDATA-API-INVALIDREQUEST","title":"Bad payload"}]}`,
	}, nil
}

func respondMethodNotAllowed() (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{
		StatusCode: http.StatusMethodNotAllowed,
		Headers:    map[string]string{"Content-Type": "application/vnd.opg-data.v1+json"},
		Body:       `{"errors":[{"code":"OPGDATA-API-METHODNOTALLOWED","title":"Method not supported"}]}`,
	}, nil
}

func respondInternalServerError(err error) (events.APIGatewayProxyResponse, error) {
	return events.APIGatewayProxyResponse{StatusCode: http.StatusInternalServerError}, err
}

func respondOK(v any) (events.APIGatewayProxyResponse, error) {
	body, _ := json.Marshal(v)
	return events.APIGatewayProxyResponse{
		StatusCode: http.StatusOK,
		Headers:    map[string]string{"Content-Type": "application/json"},
		Body:       string(body),
	}, nil
}
