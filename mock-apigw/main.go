package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/aws/aws-lambda-go/events"
)

func handler(w http.ResponseWriter, r *http.Request) {
	url := fmt.Sprintf("%s/2015-03-31/functions/function/invocations", os.Getenv("LAMBDA_URL"))

	query := map[string]string{}
	for k, v := range r.URL.Query() {
		query[k] = v[0]
	}

	var reqBody bytes.Buffer
	_, _ = io.Copy(&reqBody, r.Body)

	body := events.APIGatewayProxyRequest{
		Body:                  reqBody.String(),
		Path:                  r.URL.Path,
		HTTPMethod:            r.Method,
		MultiValueHeaders:     r.Header,
		QueryStringParameters: query,
	}

	encodedBody, _ := json.Marshal(body)

	proxyReq, err := http.NewRequest("POST", url, io.NopCloser(strings.NewReader(string(encodedBody))))
	if err != nil {
		log.Printf("error: couldn't create proxy request")
	}

	client := &http.Client{}
	resp, err := client.Do(proxyReq)

	if err != nil {
		http.Error(w, "error doing lambda request", http.StatusInternalServerError)
		return
	}

	encodedRespBody, _ := io.ReadAll(resp.Body)

	var respBody events.APIGatewayProxyResponse
	_ = json.Unmarshal(encodedRespBody, &respBody)

	if respBody.StatusCode == 0 {
		log.Print(string(encodedRespBody))
		http.Error(w, "error from lambda", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(respBody.StatusCode)
	_, err = w.Write([]byte(respBody.Body))

	if err != nil {
		log.Println("error writing response body:", err)
	}
}

func main() {
	server := &http.Server{
		Addr:              ":8080",
		Handler:           http.HandlerFunc(handler),
		ReadHeaderTimeout: 10 * time.Second,
	}

	if err := server.ListenAndServe(); err != nil {
		log.Fatal(err)
	}

	log.Println("running on port 8080")
}
