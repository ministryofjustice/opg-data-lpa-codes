package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
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

const pythonURL = "http://localhost:9009/2015-03-31/functions/function/invocations"
const golangURL = "http://localhost:9010/2015-03-31/functions/function/invocations"

func assertEqualEither(t *testing.T, expected1, expected2, actual any) bool {
	if assert.ObjectsAreEqual(expected1, actual) {
		return true
	}

	return assert.Equal(t, expected2, actual)
}

func runBoth(t *testing.T, name string, fn func(*testing.T, lambdaFn)) {
	if os.Getenv("EXCLUDE_PYTHON") != "1" {
		t.Run(name+"/python", func(t *testing.T) {
			resetDynamo()
			fn(t, callLambda(pythonURL))
		})
	}

	if os.Getenv("EXCLUDE_GOLANG") != "1" {
		t.Run(name+"/golang", func(t *testing.T) {
			resetDynamo()
			fn(t, callLambda(golangURL))
		})
	}
}

func TestHealthcheck(t *testing.T) {
	runBoth(t, "GET", func(t *testing.T, fn lambdaFn) {
		resp, _ := fn(http.MethodGet, "/v1/healthcheck", `{}`)

		assert.Equal(t, "\"OK\"", resp.Body)
		assert.Equal(t, http.StatusOK, resp.StatusCode)
	})

	runBoth(t, "HEAD", func(t *testing.T, fn lambdaFn) {
		resp, _ := fn(http.MethodHead, "/v1/healthcheck", `{}`)
		assert.Equal(t, http.StatusOK, resp.StatusCode)

		assert.Equal(t, "", resp.Body)
		assert.Equal(t, http.StatusOK, resp.StatusCode)
	})
}

func TestNotFound(t *testing.T) {
	runBoth(t, "not found", func(t *testing.T, fn lambdaFn) {
		resp, err := fn(http.MethodPost, "/v1/not-found", `{}`)
		if assert.Nil(t, err) {
			assert.Equal(t, 404, resp.StatusCode)
			assert.JSONEq(t, `{"body":{"error":{"code":"Not Found","message":"Not found url https://dev.lpa-codes.api.opg.service.justice.gov.uk/v1/not-found"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":404}`, resp.Body)
		}
	})
}

func createCode(fn lambdaFn) string {
	resp, err := fn(http.MethodPost, "/v1/create", `{"lpas":[{"lpa":"eed4f597-fd87-4536-99d0-895778824861","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","dob":"1960-06-05"}]}`)
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
	runBoth(t, "create", func(t *testing.T, fn lambdaFn) {
		resp, err := fn(http.MethodPost, "/v1/create", `{"lpas":[{"lpa":"eed4f597-fd87-4536-99d0-895778824861","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","dob":"1960-06-05"}]}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			var codes map[string][]map[string]string
			json.Unmarshal([]byte(resp.Body), &codes)
			if assert.Len(t, codes["codes"], 1) {
				assert.Equal(t, "12ad81a9-f89d-4804-99f5-7c0c8669ac9b", codes["codes"][0]["actor"])
				assert.Regexp(t, "^[0-9A-Z]{12}$", codes["codes"][0]["code"])
				assert.Equal(t, "eed4f597-fd87-4536-99d0-895778824861", codes["codes"][0]["lpa"])

				row := getCode(codes["codes"][0]["code"])
				if row == nil {
					assert.Fail(t, "code not found")
					return
				}

				assert.True(t, row.Active)
				assert.Equal(t, "12ad81a9-f89d-4804-99f5-7c0c8669ac9b", row.Actor)
				assert.Equal(t, "1960-06-05", row.DateOfBirth)
				assertEqualEither(t,
					time.Now().AddDate(1, 0, 0).Unix(),
					time.Now().AddDate(1, 0, 0).Unix()-1,
					row.ExpiryDate)
				assert.Equal(t, time.Now().Format(time.DateOnly), row.GeneratedDate)
				assert.Equal(t, time.Now().Format(time.DateOnly), row.LastUpdatedDate)
				assert.Equal(t, "eed4f597-fd87-4536-99d0-895778824861", row.LPA)
				assert.Equal(t, "Generated", row.StatusDetails)
			}
		}
	})

	runBoth(t, "create revokes previous", func(t *testing.T, fn lambdaFn) {
		oldCode := createCode(fn)

		resp, err := fn(http.MethodPost, "/v1/create", `{"lpas":[{"lpa":"eed4f597-fd87-4536-99d0-895778824861","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","dob":"1960-06-05"}]}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			var codes map[string][]map[string]string
			json.Unmarshal([]byte(resp.Body), &codes)
			if assert.Len(t, codes["codes"], 1) {
				assert.Equal(t, "12ad81a9-f89d-4804-99f5-7c0c8669ac9b", codes["codes"][0]["actor"])
				assert.Regexp(t, "^[0-9A-Z]{12}$", codes["codes"][0]["code"])
				assert.Equal(t, "eed4f597-fd87-4536-99d0-895778824861", codes["codes"][0]["lpa"])

				oldRow := getCode(oldCode)
				if oldRow == nil {
					assert.Fail(t, "old code not found")
					return
				}

				assert.False(t, oldRow.Active)
				assert.Equal(t, "12ad81a9-f89d-4804-99f5-7c0c8669ac9b", oldRow.Actor)
				assert.Equal(t, "1960-06-05", oldRow.DateOfBirth)
				assertEqualEither(t,
					time.Now().AddDate(1, 0, 0).Unix(),
					time.Now().AddDate(1, 0, 0).Unix()-1,
					oldRow.ExpiryDate)
				assert.Equal(t, time.Now().Format(time.DateOnly), oldRow.GeneratedDate)
				assert.Equal(t, time.Now().Format(time.DateOnly), oldRow.LastUpdatedDate)
				assert.Equal(t, "eed4f597-fd87-4536-99d0-895778824861", oldRow.LPA)
				assert.Equal(t, "Superseded", oldRow.StatusDetails)

				row := getCode(codes["codes"][0]["code"])
				if row == nil {
					assert.Fail(t, "code not found")
					return
				}

				assert.True(t, row.Active)
				assert.Equal(t, "12ad81a9-f89d-4804-99f5-7c0c8669ac9b", row.Actor)
				assert.Equal(t, "1960-06-05", row.DateOfBirth)
				assertEqualEither(t,
					time.Now().AddDate(1, 0, 0).Unix(),
					time.Now().AddDate(1, 0, 0).Unix()-1,
					row.ExpiryDate)
				assert.Equal(t, time.Now().Format(time.DateOnly), row.GeneratedDate)
				assert.Equal(t, time.Now().Format(time.DateOnly), row.LastUpdatedDate)
				assert.Equal(t, "eed4f597-fd87-4536-99d0-895778824861", row.LPA)
				assert.Equal(t, "Generated", row.StatusDetails)

			}
		}
	})

	runBoth(t, "create digital", func(t *testing.T, fn lambdaFn) {
		resp, err := fn(http.MethodPost, "/v1/create", `{"lpas":[{"lpa":"M-3J8F-86JF-9UDA","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","dob":"1960-06-05"}]}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			var codes map[string][]map[string]string
			json.Unmarshal([]byte(resp.Body), &codes)
			if assert.Len(t, codes["codes"], 1) {
				assert.Equal(t, "12ad81a9-f89d-4804-99f5-7c0c8669ac9b", codes["codes"][0]["actor"])
				assert.Regexp(t, "^[0-9A-Z]{12}$", codes["codes"][0]["code"])
				assert.Equal(t, "M-3J8F-86JF-9UDA", codes["codes"][0]["lpa"])

				row := getCode(codes["codes"][0]["code"])
				if row == nil {
					assert.Fail(t, "code not found")
					return
				}

				assert.True(t, row.Active)
				assert.Equal(t, time.Now().Format(time.DateOnly), row.GeneratedDate)
				assert.Equal(t, time.Now().Format(time.DateOnly), row.LastUpdatedDate)
			}
		}
	})

	testcases := map[string]string{
		"create missing lpa":   `{"lpas":[{"actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","dob":"1960-06-05"}]}`,
		"create missing actor": `{"lpas":[{"lpa":"M-3J8F-86JF-9UDA","dob":"1960-06-05"}]}`,
		"create missing dob":   `{"lpas":[{"lpa":"M-3J8F-86JF-9UDA","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b"}]}`,
		"create empty lpa":     `{"lpas":[{"lpa":"","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","dob":"1960-06-05"}]}`,
		"create empty actor":   `{"lpas":[{"lpa":"M-3J8F-86JF-9UDA","actor":"","dob":"1960-06-05"}]}`,
		"create empty dob":     `{"lpas":[{"lpa":"M-3J8F-86JF-9UDA","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","dob":""}]}`,
	}

	for name, lambdaBody := range testcases {
		runBoth(t, name, func(t *testing.T, fn lambdaFn) {
			resp, err := fn(http.MethodPost, "/v1/create", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

				assert.JSONEq(t, `{
	"body": {"error":{"code":"Bad Request","message":"Bad payload"}},
	"headers": {"Content-Type": "application/json"},
	"isBase64Encoded": false,
	"statusCode": 400
}`, resp.Body)
			}
		})
	}
}

func TestCode(t *testing.T) {
	runBoth(t, "code", func(t *testing.T, fn lambdaFn) {
		code := createCode(fn)

		resp, err := fn(http.MethodPost, "/v1/code", `{"code":"`+code+`"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			today := time.Now().Format(time.DateOnly)
			expires := time.Now().AddDate(1, 0, 0).Unix()
			assertEqualEither(t,
				fmt.Sprintf(`[{"active":true,"actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","code":"%[1]s","dob":"1960-06-05","expiry_date":%[3]d,"generated_date":"%[2]s","last_updated_date":"%[2]s","lpa":"eed4f597-fd87-4536-99d0-895778824861","status_details":"Generated"}]`, code, today, expires),
				fmt.Sprintf(`[{"active":true,"actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b","code":"%[1]s","dob":"1960-06-05","expiry_date":%[3]d,"generated_date":"%[2]s","last_updated_date":"%[2]s","lpa":"eed4f597-fd87-4536-99d0-895778824861","status_details":"Generated"}]`, code, today, expires-1),
				resp.Body)
		}
	})

	runBoth(t, "not found", func(t *testing.T, fn lambdaFn) {
		resp, err := fn(http.MethodPost, "/v1/code", `{"code":"abcd1234abcd"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusNotFound, resp.StatusCode)

			assert.Equal(t, `{"body":{"error":{"code":"Not Found","message":"Not found url https://dev.lpa-codes.api.opg.service.justice.gov.uk/v1/code"}},"headers":{"Content-Type":"application/json"},"isBase64Encoded":false,"statusCode":404}`, resp.Body)
		}
	})
}

func TestExists(t *testing.T) {
	runBoth(t, "exists", func(t *testing.T, fn lambdaFn) {
		_ = createCode(fn)

		resp, err := fn(http.MethodPost, "/v1/exists", `{"lpa":"eed4f597-fd87-4536-99d0-895778824861","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.Regexp(t, `\{"Created":"[0-9]{4}-[0-9]{2}-[0-9]{2}"\}`, resp.Body)
		}
	})

	runBoth(t, "does not exist", func(t *testing.T, fn lambdaFn) {
		resp, err := fn(http.MethodPost, "/v1/exists", `{"lpa":"eed4f597-fd87-4536-99d0-895778824861","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)

			assert.Equal(t, `{"Created":null}`, resp.Body)
		}
	})

	testcases := map[string]string{
		"missing lpa":   `{"actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b"}`,
		"missing actor": `{"lpa":"eed4f597-fd87-4536-99d0-895778824861"}`,
		"empty lpa":     `{"lpa":"","actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b"}`,
		"empty actor":   `{"lpa":"eed4f597-fd87-4536-99d0-895778824861","actor":""}`,
	}

	for name, lambdaBody := range testcases {
		runBoth(t, name, func(t *testing.T, fn lambdaFn) {
			resp, err := fn(http.MethodPost, "/v1/exists", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

				assert.JSONEq(t, `{
	"body": {"error":{"code":"Bad Request","message":"Bad payload"}},
	"headers": {"Content-Type": "application/json"},
	"isBase64Encoded": false,
	"statusCode": 400
}`, resp.Body)
			}
		})
	}
}

func TestMarkUsed(t *testing.T) {
	runBoth(t, "mark used", func(t *testing.T, fn lambdaFn) {
		code := createCode(fn)

		row := getCode(code)
		if row == nil {
			assert.Fail(t, "row not found")
			return
		}

		resp, err := fn(http.MethodPost, "/v1/mark_used", `{"code":"`+code+`"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"codes marked used":1}`, resp.Body)

			row := getCode(code)
			if row == nil {
				assert.Fail(t, "row not found")
				return
			}

			assert.False(t, row.Active)

			seconds := time.Now().AddDate(2, 0, 0).Unix()
			assertEqualEither(t,
				seconds,
				seconds-1,
				row.ExpiryDate)
		}
	})

	testcases := map[string]string{
		"empty code":   `{"code":""}`,
		"missing code": `{"banana":"chipmunk"}`,
	}

	for name, lambdaBody := range testcases {
		runBoth(t, name, func(t *testing.T, fn lambdaFn) {
			resp, err := fn(http.MethodPost, "/v1/mark_used", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
				assert.JSONEq(t, `{
	"body": {"error":{"code":"Bad Request","message":"Bad payload"}},
	"headers": {"Content-Type": "application/json"},
	"isBase64Encoded": false,
	"statusCode": 400
}`, resp.Body)
			}
		})
	}
}

func TestRevoke(t *testing.T) {
	runBoth(t, "revoke", func(t *testing.T, fn lambdaFn) {
		code := createCode(fn)

		resp, err := fn(http.MethodPost, "/v1/revoke", `{"code":"`+code+`"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"codes revoked":1}`, resp.Body)

			row := getCode(code)
			if row == nil {
				assert.Fail(t, "row not found")
				return
			}

			assert.False(t, row.Active)
			assert.Equal(t, "Revoked", row.StatusDetails)
		}
	})

	testcases := map[string]string{
		"empty code":   `{"code":""}`,
		"missing code": `{"banana":"chipmunk"}`,
	}

	for name, lambdaBody := range testcases {
		runBoth(t, name, func(t *testing.T, fn lambdaFn) {
			resp, err := fn(http.MethodPost, "/v1/revoke", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
				assert.JSONEq(t, `{
	"body": {"error":{"code":"Bad Request","message":"Bad payload"}},
	"headers": {"Content-Type": "application/json"},
	"isBase64Encoded": false,
	"statusCode": 400
}`, resp.Body)
			}
		})
	}
}

func TestValidate(t *testing.T) {
	runBoth(t, "validate", func(t *testing.T, fn lambdaFn) {
		code := createCode(fn)

		resp, err := fn(http.MethodPost, "/v1/validate", `{"code":"`+code+`","lpa":"eed4f597-fd87-4536-99d0-895778824861","dob":"1960-06-05"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"actor":"12ad81a9-f89d-4804-99f5-7c0c8669ac9b"}`, resp.Body)
		}
	})

	runBoth(t, "wrong code", func(t *testing.T, fn lambdaFn) {
		resp, err := fn(http.MethodPost, "/v1/validate", `{"code":"whatever","lpa":"eed4f597-fd87-4536-99d0-895778824861","dob":"1960-06-05"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"actor":null}`, resp.Body)
		}
	})

	runBoth(t, "wrong lpa", func(t *testing.T, fn lambdaFn) {
		code := createCode(fn)

		resp, err := fn(http.MethodPost, "/v1/validate", `{"code":"`+code+`","lpa":"whatever","dob":"1960-06-05"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"actor":null}`, resp.Body)
		}
	})

	runBoth(t, "wrong dob", func(t *testing.T, fn lambdaFn) {
		code := createCode(fn)

		resp, err := fn(http.MethodPost, "/v1/validate", `{"code":"`+code+`","lpa":"eed4f597-fd87-4536-99d0-895778824861","dob":"1961-01-01"}`)
		if assert.Nil(t, err) {
			assert.Equal(t, http.StatusOK, resp.StatusCode)
			assert.JSONEq(t, `{"actor":null}`, resp.Body)
		}
	})

	testcases := map[string]string{
		"missing code": `{"lpa":"eed4f597-fd87-4536-99d0-895778824861","dob":"1960-06-05"}`,
		"missing lpa":  `{"code":"hdgeytkvnshd","dob":"1960-06-05"}`,
		"missing dob":  `{"code":"hdgeytkvnshd","lpa":"eed4f597-fd87-4536-99d0-895778824861"}`,
		"empty code":   `{"code":"","lpa":"eed4f597-fd87-4536-99d0-895778824861","dob":"1960-06-05"}`,
		"empty lpa":    `{"code":"hdgeytkvnshd","lpa":"","dob":"1960-06-05"}`,
		"empty dob":    `{"code":"hdgeytkvnshd","lpa":"eed4f597-fd87-4536-99d0-895778824861","dob":""}`,
	}

	for name, lambdaBody := range testcases {
		runBoth(t, name, func(t *testing.T, fn lambdaFn) {
			resp, err := fn(http.MethodPost, "/v1/validate", lambdaBody)
			if assert.Nil(t, err) {
				assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
				assert.JSONEq(t, `{
	"body": {"error":{"code":"Bad Request","message":"Bad payload"}},
	"headers": {"Content-Type": "application/json"},
	"isBase64Encoded": false,
	"statusCode": 400
}`, resp.Body)
			}
		})
	}
}

type lambdaFn func(method, path, body string) (*lambdaResponse, error)

type lambdaResponse struct {
	StatusCode int               `json:"statusCode"`
	Headers    map[string]string `json:"headers"`
	Body       string            `json:"body"`
}

func callLambda(url string) lambdaFn {
	return func(method, path, body string) (*lambdaResponse, error) {
		data := toLambdaRequest(method, path, body)

		req, _ := http.NewRequest(http.MethodPost, url, data)
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
	if _, err := db.DeleteTable(ctx, &dynamodb.DeleteTableInput{
		TableName: aws.String("lpa-codes-local"),
	}); err != nil {
		var exception *types.ResourceNotFoundException
		if !errors.As(err, &exception) {
			panic(err)
		}
	}

	if _, err := db.CreateTable(ctx, &dynamodb.CreateTableInput{
		TableName: aws.String("lpa-codes-local"),
		AttributeDefinitions: []types.AttributeDefinition{
			{AttributeName: aws.String("code"), AttributeType: types.ScalarAttributeTypeS},
			{AttributeName: aws.String("lpa"), AttributeType: types.ScalarAttributeTypeS},
			{AttributeName: aws.String("actor"), AttributeType: types.ScalarAttributeTypeS},
		},
		KeySchema: []types.KeySchemaElement{
			{AttributeName: aws.String("code"), KeyType: types.KeyTypeHash},
		},
		GlobalSecondaryIndexes: []types.GlobalSecondaryIndex{{
			IndexName: aws.String("key_index"),
			KeySchema: []types.KeySchemaElement{
				{AttributeName: aws.String("lpa"), KeyType: types.KeyTypeHash},
				{AttributeName: aws.String("actor"), KeyType: types.KeyTypeRange},
			},
			Projection: &types.Projection{ProjectionType: types.ProjectionTypeAll},
			ProvisionedThroughput: &types.ProvisionedThroughput{
				ReadCapacityUnits:  aws.Int64(5),
				WriteCapacityUnits: aws.Int64(5),
			},
		}},
		ProvisionedThroughput: &types.ProvisionedThroughput{
			ReadCapacityUnits:  aws.Int64(5),
			WriteCapacityUnits: aws.Int64(5),
		},
	}); err != nil {
		panic(err)
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
