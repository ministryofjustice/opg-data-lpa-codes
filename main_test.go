package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/feature/dynamodb/attributevalue"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
	"github.com/stretchr/testify/assert"
)

var (
	ctx = context.Background()
	db  *dynamodb.Client
)

func init() {
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		panic(err)
	}

	cfg.BaseEndpoint = aws.String("http://localhost:8000")

	db = dynamodb.NewFromConfig(cfg)
}

func assertEqualEither(t *testing.T, expected1, expected2, actual any) bool {
	if assert.ObjectsAreEqual(expected1, actual) {
		return true
	}

	return assert.Equal(t, expected2, actual)
}

func runTest(t *testing.T, name string, fn func(*testing.T)) {
	t.Run(name, func(t *testing.T) {
		resetDynamo()
		fn(t)
	})
}

func TestHealthcheck(t *testing.T) {
	t.Run("GET", func(t *testing.T) {
		resp, _ := callLambda(http.MethodGet, "/v1/healthcheck", `{}`)

		assert.Equal(t, "\"OK\"", resp.Body)
		assert.Equal(t, http.StatusOK, resp.StatusCode)
	})

	t.Run("HEAD", func(t *testing.T) {
		resp, _ := callLambda(http.MethodHead, "/v1/healthcheck", `{}`)
		assert.Equal(t, http.StatusOK, resp.StatusCode)

		assert.Equal(t, "", resp.Body)
		assert.Equal(t, http.StatusOK, resp.StatusCode)
	})
}

func TestNotFound(t *testing.T) {
	resp, err := callLambda(http.MethodPost, "/v1/not-found", `{}`)
	if assert.Nil(t, err) {
		assert.Equal(t, http.StatusNotFound, resp.StatusCode)
		assert.JSONEq(t, `{"body":{"error":{"code":"Not Found","message":"Not found url https://dev.lpa-codes.api.opg.service.justice.gov.uk/v1/not-found"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":404}`, resp.Body)
	}
}

func TestMethodNotAllowed(t *testing.T) {
	postRoutes := []string{
		"/v1/create",
		"/v1/exists",
		"/v1/revoke",
		"/v1/validate",
		"/v1/code",
		"/v1/paper-verification-code",
		"/v1/paper-verification-code/validate",
		"/v1/paper-verification-code/expire",
	}

	for _, url := range postRoutes {
		t.Run("get "+url, func(t *testing.T) {
			resp, err := callLambda(http.MethodGet, url, `{}`)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusMethodNotAllowed, resp.StatusCode)
				assert.JSONEq(t, `{"body":{"error":{"code":"Method Not Allowed","message":"Method not supported"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":405}`, resp.Body)
			}
		})
	}
}

const (
	createCodeLegacy    = `{"lpas":[{"lpa":"700000000001","actor":"700000000002","dob":"1960-06-05"}]}`
	createCodeModernise = `{"lpas":[{"lpa":"M-1234-1234-1234","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","dob":"1960-06-05"}]}`
)

func createCode(body string) string {
	resp, err := callLambda(http.MethodPost, "/v1/create", body)
	if err != nil {
		return ""
	}

	var codes struct {
		Codes []struct {
			Code string `json:"code"`
		} `json:"codes"`
	}
	json.Unmarshal([]byte(resp.Body), &codes)

	if len(codes.Codes) == 0 {
		log.Printf("create code got: %d", resp.StatusCode)
		return ""
	}

	for range 5 {
		time.Sleep(100 * time.Millisecond)

		if getCode(codes.Codes[0].Code) != nil {
			break
		}
	}

	return codes.Codes[0].Code
}

func TestCreate(t *testing.T) {
	runTest(t, "create", func(t *testing.T) {
		resp, err := callLambda(http.MethodPost, "/v1/create", createCodeLegacy)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			var codes map[string][]map[string]string
			json.Unmarshal([]byte(resp.Body), &codes)
			if assert.Len(t, codes["codes"], 1) {
				assert.Equal(t, "700000000002", codes["codes"][0]["actor"])
				assert.Regexp(t, "^[0-9A-Z]{12}$", codes["codes"][0]["code"])
				assert.Equal(t, "700000000001", codes["codes"][0]["lpa"])

				assertCode(t, Row{
					Active:          true,
					Actor:           "700000000002",
					DateOfBirth:     "1960-06-05",
					ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
					GeneratedDate:   time.Now().Format(time.DateOnly),
					LastUpdatedDate: time.Now().Format(time.DateOnly),
					LPA:             "700000000001",
					StatusDetails:   "Generated",
				}, codes["codes"][0]["code"])
			}
		}
	})

	runTest(t, "create multiple", func(t *testing.T) {
		resp, err := callLambda(http.MethodPost, "/v1/create", `{"lpas":[{"lpa":"700000000001","actor":"700000000002","dob":"1960-06-05"},{"lpa":"700000000003","actor":"700000000004","dob":"1960-06-06"}]}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			var codes map[string][]map[string]string
			json.Unmarshal([]byte(resp.Body), &codes)
			if assert.Len(t, codes["codes"], 2) {
				assert.Equal(t, "700000000002", codes["codes"][0]["actor"])
				assert.Regexp(t, "^[0-9A-Z]{12}$", codes["codes"][0]["code"])
				assert.Equal(t, "700000000001", codes["codes"][0]["lpa"])

				assertCode(t, Row{
					Active:          true,
					Actor:           "700000000002",
					DateOfBirth:     "1960-06-05",
					ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
					GeneratedDate:   time.Now().Format(time.DateOnly),
					LastUpdatedDate: time.Now().Format(time.DateOnly),
					LPA:             "700000000001",
					StatusDetails:   "Generated",
				}, codes["codes"][0]["code"])

				assert.Equal(t, "700000000004", codes["codes"][1]["actor"])
				assert.Regexp(t, "^[0-9A-Z]{12}$", codes["codes"][1]["code"])
				assert.Equal(t, "700000000003", codes["codes"][1]["lpa"])

				assertCode(t, Row{
					Active:          true,
					Actor:           "700000000004",
					DateOfBirth:     "1960-06-06",
					ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
					GeneratedDate:   time.Now().Format(time.DateOnly),
					LastUpdatedDate: time.Now().Format(time.DateOnly),
					LPA:             "700000000003",
					StatusDetails:   "Generated",
				}, codes["codes"][1]["code"])
			}
		}
	})

	runTest(t, "create revokes previous", func(t *testing.T) {
		oldCode := createCode(createCodeLegacy)

		resp, err := callLambda(http.MethodPost, "/v1/create", createCodeLegacy)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			var codes map[string][]map[string]string
			json.Unmarshal([]byte(resp.Body), &codes)
			if assert.Len(t, codes["codes"], 1) {
				assert.Equal(t, "700000000002", codes["codes"][0]["actor"])
				assert.Regexp(t, "^[0-9A-Z]{12}$", codes["codes"][0]["code"])
				assert.Equal(t, "700000000001", codes["codes"][0]["lpa"])

				assertCode(t, Row{
					Active:          false,
					Actor:           "700000000002",
					DateOfBirth:     "1960-06-05",
					ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
					GeneratedDate:   time.Now().Format(time.DateOnly),
					LastUpdatedDate: time.Now().Format(time.DateOnly),
					LPA:             "700000000001",
					StatusDetails:   "Superseded",
				}, oldCode)

				assertCode(t, Row{
					Active:          true,
					Actor:           "700000000002",
					DateOfBirth:     "1960-06-05",
					ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
					GeneratedDate:   time.Now().Format(time.DateOnly),
					LastUpdatedDate: time.Now().Format(time.DateOnly),
					LPA:             "700000000001",
					StatusDetails:   "Generated",
				}, codes["codes"][0]["code"])
			}
		}
	})

	runTest(t, "create modernise", func(t *testing.T) {
		resp, err := callLambda(http.MethodPost, "/v1/create", createCodeModernise)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			var codes map[string][]map[string]string
			json.Unmarshal([]byte(resp.Body), &codes)
			if assert.Len(t, codes["codes"], 1) {
				assert.Equal(t, "12ad81a9-f89d-4804-99f5-7c0c8669ac9b", codes["codes"][0]["actor"])
				assert.Regexp(t, "^[0-9A-Z]{12}$", codes["codes"][0]["code"])
				assert.Equal(t, "M-1234-1234-1234", codes["codes"][0]["lpa"])

				assertCode(t, Row{
					Active:          true,
					Actor:           "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
					DateOfBirth:     "1960-06-05",
					ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
					GeneratedDate:   time.Now().Format(time.DateOnly),
					LastUpdatedDate: time.Now().Format(time.DateOnly),
					LPA:             "M-1234-1234-1234",
					StatusDetails:   "Generated",
				}, codes["codes"][0]["code"])
			}
		}
	})

	runTest(t, "create modernise revokes previous", func(t *testing.T) {
		oldCode := createCode(createCodeModernise)

		resp, err := callLambda(http.MethodPost, "/v1/create", createCodeModernise)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			var codes map[string][]map[string]string
			json.Unmarshal([]byte(resp.Body), &codes)
			if assert.Len(t, codes["codes"], 1) {
				assert.Equal(t, "12ad81a9-f89d-4804-99f5-7c0c8669ac9b", codes["codes"][0]["actor"])
				assert.Regexp(t, "^[0-9A-Z]{12}$", codes["codes"][0]["code"])
				assert.Equal(t, "M-1234-1234-1234", codes["codes"][0]["lpa"])

				assertCode(t, Row{
					Active:          false,
					Actor:           "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
					DateOfBirth:     "1960-06-05",
					ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
					GeneratedDate:   time.Now().Format(time.DateOnly),
					LastUpdatedDate: time.Now().Format(time.DateOnly),
					LPA:             "M-1234-1234-1234",
					StatusDetails:   "Superseded",
				}, oldCode)

				assertCode(t, Row{
					Active:          true,
					Actor:           "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
					DateOfBirth:     "1960-06-05",
					ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
					GeneratedDate:   time.Now().Format(time.DateOnly),
					LastUpdatedDate: time.Now().Format(time.DateOnly),
					LPA:             "M-1234-1234-1234",
					StatusDetails:   "Generated",
				}, codes["codes"][0]["code"])
			}
		}
	})

	testcases := map[string]string{
		"create missing lpa":   `{"lpas":[{"actor":"700000000002","dob":"1960-06-05"}]}`,
		"create missing actor": `{"lpas":[{"lpa":"M-1234-1234-1234","dob":"1960-06-05"}]}`,
		"create missing dob":   `{"lpas":[{"lpa":"M-1234-1234-1234","actor":"700000000002"}]}`,
		"create empty lpa":     `{"lpas":[{"lpa":"","actor":"700000000002","dob":"1960-06-05"}]}`,
		"create empty actor":   `{"lpas":[{"lpa":"M-1234-1234-1234","actor":"","dob":"1960-06-05"}]}`,
		"create empty dob":     `{"lpas":[{"lpa":"M-1234-1234-1234","actor":"700000000002","dob":""}]}`,
	}

	for name, lambdaBody := range testcases {
		t.Run(name, func(t *testing.T) {
			resp, err := callLambda(http.MethodPost, "/v1/create", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

				assert.JSONEq(t, `{"body":{"error":{"code":"Bad Request","message":"Bad payload"}},"headers":{"Content-Type": "application/json"},"isBase64Encoded":false,"statusCode":400}`, resp.Body)
			}
		})
	}
}

func TestCode(t *testing.T) {
	runTest(t, "code", func(t *testing.T) {
		code := createCode(createCodeLegacy)

		resp, err := callLambda(http.MethodPost, "/v1/code", `{"code":"`+code+`"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			today := time.Now().Format(time.DateOnly)
			expires := time.Now().AddDate(1, 0, 0).Unix()
			assertEqualEither(t,
				fmt.Sprintf(`[{"active":true,"actor":"700000000002","code":"%[1]s","dob":"1960-06-05","expiry_date":%[3]d,"generated_date":"%[2]s","last_updated_date":"%[2]s","lpa":"700000000001","status_details":"Generated"}]`, code, today, expires),
				fmt.Sprintf(`[{"active":true,"actor":"700000000002","code":"%[1]s","dob":"1960-06-05","expiry_date":%[3]d,"generated_date":"%[2]s","last_updated_date":"%[2]s","lpa":"700000000001","status_details":"Generated"}]`, code, today, expires-1),
				resp.Body)
		}
	})

	runTest(t, "not found", func(t *testing.T) {
		resp, err := callLambda(http.MethodPost, "/v1/code", `{"code":"abcd1234abcd"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusNotFound, resp.StatusCode)

			assert.Equal(t, `{"body":{"error":{"code":"Not Found","message":"Not found url https://dev.lpa-codes.api.opg.service.justice.gov.uk/v1/code"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":404}`, resp.Body)
		}
	})

	testcases := map[string]string{
		"missing lpa": `{}`,
		"empty":       `{"code":""}`,
	}

	for name, lambdaBody := range testcases {
		t.Run(name, func(t *testing.T) {
			resp, err := callLambda(http.MethodPost, "/v1/code", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

				assert.Equal(t, `{"body":{"error":{"code":"Bad Request","message":"Bad payload"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":400}`, resp.Body)
			}
		})
	}
}

func TestExists(t *testing.T) {
	runTest(t, "exists", func(t *testing.T) {
		_ = createCode(createCodeLegacy)

		resp, err := callLambda(http.MethodPost, "/v1/exists", `{"lpa":"700000000001","actor":"700000000002"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.Equal(t, `{"Created":"`+time.Now().Format(time.DateOnly)+`"}`, resp.Body)
		}
	})

	runTest(t, "inactive", func(t *testing.T) {
		code := createCode(createCodeLegacy)

		if _, err := callLambda(http.MethodPost, "/v1/revoke", `{"code":"`+code+`"}`); !assert.Nil(t, err) {
			return
		}

		resp, err := callLambda(http.MethodPost, "/v1/exists", `{"lpa":"700000000001","actor":"700000000002"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.Equal(t, `{"Created":null}`, resp.Body)
		}
	})

	runTest(t, "does not exist", func(t *testing.T) {
		resp, err := callLambda(http.MethodPost, "/v1/exists", `{"lpa":"700000000001","actor":"700000000002"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			assert.Equal(t, `{"Created":null}`, resp.Body)
		}
	})

	testcases := map[string]string{
		"missing lpa":   `{"actor":"700000000002"}`,
		"missing actor": `{"lpa":"700000000001"}`,
		"empty lpa":     `{"lpa":"","actor":"700000000002"}`,
		"empty actor":   `{"lpa":"700000000001","actor":""}`,
	}

	for name, lambdaBody := range testcases {
		t.Run(name, func(t *testing.T) {
			resp, err := callLambda(http.MethodPost, "/v1/exists", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

				assert.JSONEq(t, `{"body":{"error":{"code":"Bad Request","message":"Bad payload"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":400}`, resp.Body)
			}
		})
	}
}

func TestRevoke(t *testing.T) {
	runTest(t, "revoke", func(t *testing.T) {
		code := createCode(createCodeLegacy)

		resp, err := callLambda(http.MethodPost, "/v1/revoke", `{"code":"`+code+`"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"codes revoked":1}`, resp.Body)

			assertCode(t, Row{
				Active:          false,
				Actor:           "700000000002",
				DateOfBirth:     "1960-06-05",
				ExpiryDate:      time.Now().AddDate(1, 0, 0).Unix(),
				GeneratedDate:   time.Now().Format(time.DateOnly),
				LastUpdatedDate: time.Now().Format(time.DateOnly),
				LPA:             "700000000001",
				StatusDetails:   "Revoked",
			}, code)
		}
	})

	runTest(t, "wrong code", func(t *testing.T) {
		resp, err := callLambda(http.MethodPost, "/v1/revoke", `{"code":"something"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"codes revoked":0}`, resp.Body)
		}
	})

	testcases := map[string]string{
		"empty code":   `{"code":""}`,
		"missing code": `{"banana":"chipmunk"}`,
	}

	for name, lambdaBody := range testcases {
		t.Run(name, func(t *testing.T) {
			resp, err := callLambda(http.MethodPost, "/v1/revoke", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
				assert.JSONEq(t, `{"body":{"error":{"code":"Bad Request","message":"Bad payload"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":400}`, resp.Body)
			}
		})
	}
}

func TestValidate(t *testing.T) {
	runTest(t, "validate", func(t *testing.T) {
		code := createCode(createCodeLegacy)

		resp, err := callLambda(http.MethodPost, "/v1/validate", `{"code":"`+code+`","lpa":"700000000001","dob":"1960-06-05"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"actor":"700000000002"}`, resp.Body)
		}
	})

	runTest(t, "wrong code", func(t *testing.T) {
		resp, err := callLambda(http.MethodPost, "/v1/validate", `{"code":"whatever","lpa":"700000000001","dob":"1960-06-05"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"actor":null}`, resp.Body)
		}
	})

	runTest(t, "wrong lpa", func(t *testing.T) {
		code := createCode(createCodeLegacy)

		resp, err := callLambda(http.MethodPost, "/v1/validate", `{"code":"`+code+`","lpa":"whatever","dob":"1960-06-05"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"actor":null}`, resp.Body)
		}
	})

	runTest(t, "wrong dob", func(t *testing.T) {
		code := createCode(createCodeLegacy)

		resp, err := callLambda(http.MethodPost, "/v1/validate", `{"code":"`+code+`","lpa":"700000000001","dob":"1961-01-01"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"actor":null}`, resp.Body)
		}
	})

	runTest(t, "inactive", func(t *testing.T) {
		code := createCode(createCodeLegacy)

		if _, err := callLambda(http.MethodPost, "/v1/revoke", `{"code":"`+code+`"}`); !assert.Nil(t, err) {
			return
		}

		resp, err := callLambda(http.MethodPost, "/v1/validate", `{"code":"`+code+`","lpa":"700000000001","dob":"1960-06-05"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"actor":null}`, resp.Body)
		}
	})

	testcases := map[string]string{
		"missing code": `{"lpa":"700000000001","dob":"1960-06-05"}`,
		"missing lpa":  `{"code":"hdgeytkvnshd","dob":"1960-06-05"}`,
		"missing dob":  `{"code":"hdgeytkvnshd","lpa":"700000000001"}`,
		"empty code":   `{"code":"","lpa":"700000000001","dob":"1960-06-05"}`,
		"empty lpa":    `{"code":"hdgeytkvnshd","lpa":"","dob":"1960-06-05"}`,
		"empty dob":    `{"code":"hdgeytkvnshd","lpa":"700000000001","dob":""}`,
	}

	for name, lambdaBody := range testcases {
		t.Run(name, func(t *testing.T) {
			resp, err := callLambda(http.MethodPost, "/v1/validate", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
				assert.JSONEq(t, `{"body":{"error":{"code":"Bad Request","message":"Bad payload"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":400}`, resp.Body)
			}
		})
	}
}

func TestPaperVerificationCode(t *testing.T) {
	resp, err := callLambda(http.MethodPost, "/v1/paper-verification-code", `{}`)
	if assert.Nil(t, err) {
		assert.Equal(t, http.StatusInternalServerError, resp.StatusCode)
		assert.Equal(t, ``, resp.Body)
	}
}

func TestPaperVerificationCodeValidate(t *testing.T) {
	resp, err := callLambda(http.MethodPost, "/v1/paper-verification-code/validate", `{}`)
	if assert.Nil(t, err) {
		assert.Equal(t, http.StatusInternalServerError, resp.StatusCode)
		assert.Equal(t, ``, resp.Body)
	}
}

func TestPaperVerificationCodeExpire(t *testing.T) {
	resp, err := callLambda(http.MethodPost, "/v1/paper-verification-code/expire", `{}`)
	if assert.Nil(t, err) {
		assert.Equal(t, http.StatusInternalServerError, resp.StatusCode)
		assert.Equal(t, ``, resp.Body)
	}
}

type lambdaFn func(method, path, body string) (*lambdaResponse, error)

type lambdaResponse struct {
	StatusCode int               `json:"statusCode"`
	Headers    map[string]string `json:"headers"`
	Body       string            `json:"body"`
}

func callLambda(method, path, body string) (*lambdaResponse, error) {
	data := toLambdaRequest(method, path, body)

	req, _ := http.NewRequest(http.MethodPost, "http://localhost:8081/2015-03-31/functions/function/invocations", data)
	req.Header.Add("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("lambda returned %d", resp.StatusCode)
	}

	var v lambdaResponse
	if err := json.NewDecoder(resp.Body).Decode(&v); err != nil {
		return nil, err
	}

	v.Body = strings.TrimSpace(v.Body)
	return &v, nil
}

func toLambdaRequest(method, path, body string) io.Reader {
	encBody, _ := json.Marshal(body)
	resource := strings.TrimPrefix(path, "/v1")

	return strings.NewReader(`{
	"body": ` + string(encBody) + `,
	"queryStringParameters": null,
	"httpMethod": "` + method + `",
	"path": "` + path + `",
	"isBase64Encoded": false,
	"resource": "` + resource + `",
	"requestContext": {
		"requestTime": "07/May/2022:09:59:31 +0000",
		"protocol": "HTTP/1.1",
		"domainName": "dev.lpa-codes.api.opg.service.justice.gov.uk",
		"resourceId": "redacted",
		"apiId": "redacted",
		"operationName": "app.addReportDocument",
		"resourcePath": "` + resource + `",
		"httpMethod": "` + method + `",
		"domainPrefix": "dev",
		"requestId": "5bddb576-db04-4322-9c09-75e00c8a549e",
		"extendedRequestId": "Rv9opGq5joEFdFg=",
		"path": "` + path + `",
		"stage": "v1",
		"requestTimeEpoch": 1651917571921,
		"identity": {
			"userArn": "arn:aws:sts::288342028542:assumed-role/operator/lpa_codes_script",
			"user": "redacted:lpa_codes_script",
			"cognitoIdentityPoolId": null,
			"userAgent": "python-requests/2.24.0",
			"accountId": "288342028542",
			"principalOrgId": "redacted",
			"accessKey": "redacted",
			"caller": "redacted:lpa_codes_script",
			"cognitoIdentityId": null,
			"cognitoAuthenticationType": null,
			"sourceIp": "redacted",
			"cognitoAuthenticationProvider": null
		},
		"accountId": "288342028542"
	},
	"multiValueHeaders": {
		"Accept-Encoding": ["gzip, deflate"],
		"X-Forwarded-Port": ["443"],
		"X-Amzn-Trace-Id": ["redacted"],
		"x-amz-date": ["20220507T095931Z"],
		"x-amz-content-sha256": ["redacted"],
		"X-Forwarded-For": ["redacted"],
		"Accept": ["*/*"],
		"User-Agent": ["python-requests/2.24.0"],
		"Host": ["dev.lpa-codes.api.opg.service.justice.gov.uk"],
		"X-Forwarded-Proto": ["https"],
		"x-amz-security-token": ["redacted"],
		"content-type": ["application/json; charset=utf-8"]
	},
	"multiValueQueryStringParameters": null,
	"headers": {
		"Accept-Encoding": "gzip, deflate",
		"X-Forwarded-Port": "443",
		"X-Amzn-Trace-Id": "redacted",
		"x-amz-date": "20220507T095931Z",
		"x-amz-content-sha256": "redacted",
		"X-Forwarded-For": "redacted",
		"Accept": "*/*",
		"User-Agent": "python-requests/2.24.0",
		"Host": "dev.lpa-codes.api.opg.service.justice.gov.uk",
		"X-Forwarded-Proto": "https",
		"x-amz-security-token": "redacted",
		"content-type": "application/json; charset=utf-8"
	}
}`)
}

type Row struct {
	Active          bool   `dynamodbav:"active"`
	Actor           string `dynamodbav:"actor"`
	Code            string `dynamodbav:"code"`
	DateOfBirth     string `dynamodbav:"dob"`
	ExpiryDate      int64  `dynamodbav:"expiry_date"`
	GeneratedDate   string `dynamodbav:"generated_date"`
	LastUpdatedDate string `dynamodbav:"last_updated_date"`
	LPA             string `dynamodbav:"lpa"`
	StatusDetails   string `dynamodbav:"status_details"`
}

func resetDynamo() {
	resp, err := http.Post("http://localhost:8080/reset-database", "", nil)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		panic(body)
	}
}

func getCode(code string) *Row {
	output, err := db.GetItem(ctx, &dynamodb.GetItemInput{
		Key: map[string]types.AttributeValue{
			"code": &types.AttributeValueMemberS{Value: code},
		},
		TableName: aws.String("lpa-codes-local"),
	})
	if err != nil || output.Item == nil {
		return nil
	}

	var v Row
	attributevalue.UnmarshalMap(output.Item, &v)
	return &v
}

func assertCode(t *testing.T, expected Row, code string) bool {
	row := getCode(code)
	if row == nil {
		assert.Failf(t, "code not found: %s", code)
		return false
	}

	// don't worry about providing the code for asserting
	expected.Code = code
	// do the minus case, to account for the passing of time, first so we get the
	// error from the "normal" assertion
	expected.ExpiryDate -= 1

	if assert.ObjectsAreEqual(expected, *row) {
		return true
	}

	expected.ExpiryDate += 1
	return assert.Equal(t, expected, *row)
}
