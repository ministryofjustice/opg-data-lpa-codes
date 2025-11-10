package codes

import (
	"context"
	"io"
	"net/http"
	"os"
	"testing"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
	"github.com/stretchr/testify/assert"
)

func TestPaperVerificationCodeStore_Create(t *testing.T) {
	ctx := context.Background()

	resp, err := http.Post("http://localhost:8080/_reset_database", "", nil)
	if err != nil {
		t.Skip("environment must be running for this test")
		return
	}
	if !assert.Equal(t, http.StatusOK, resp.StatusCode) {
		io.Copy(os.Stderr, resp.Body)
		return
	}

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		t.Skip("environment must be running for this test")
		return
	}
	cfg.BaseEndpoint = aws.String("http://localhost:8000")

	store := NewPaperVerificationCodeStore(dynamodb.NewFromConfig(cfg), "data-lpa-codes-local")

	codesGenerated := 0
	store.generateCode = func() string {
		codesGenerated++

		if codesGenerated > 15 {
			return "P-4567-4567-4567-45"
		}

		return "P-1234-1234-1234-12"
	}

	created, err := store.Create(ctx, Key{Actor: "test", LPA: "test"})
	assert.NoError(t, err)
	assert.Equal(t, "P-1234-1234-1234-12", created.Code())

	_, err = store.Create(ctx, Key{Actor: "test", LPA: "test"})
	var ccfe *types.ConditionalCheckFailedException
	assert.ErrorAs(t, err, &ccfe)
	assert.Equal(t, 11, codesGenerated)

	created2, err := store.Create(ctx, Key{Actor: "test", LPA: "test"})
	assert.NoError(t, err)
	assert.Equal(t, "P-4567-4567-4567-45", created2.Code())
	assert.Equal(t, 16, codesGenerated)
}
