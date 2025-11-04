package codes

import (
	"context"
	"net/http"
	"testing"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/stretchr/testify/assert"
)

func TestActivationCodeStore_GenerateCode(t *testing.T) {
	ctx := context.Background()

	_, err := http.Post("http://localhost:8080/reset-database", "", nil)
	if err != nil {
		t.Skip("environment must be running for this test")
		return
	}

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		t.Skip("environment must be running for this test")
		return
	}
	cfg.BaseEndpoint = aws.String("http://localhost:8000")

	store := NewActivationCodeStore(dynamodb.NewFromConfig(cfg), "lpa-codes-local")

	codesGenerated := 0
	store.generateCode = func() string {
		codesGenerated++

		if codesGenerated > 15 {
			return "P-4567-4567-4567-45"
		}

		return "P-1234-1234-1234-12"
	}

	code, err := store.GenerateCode(ctx)
	assert.NoError(t, err)
	_, err = store.InsertNewCode(ctx, Key{Actor: "test", LPA: "test"}, "1970-01-01", code)
	assert.NoError(t, err)

	_, err = store.GenerateCode(ctx)
	assert.ErrorContains(t, err, "generate code reached max attempts")
	assert.Equal(t, 11, codesGenerated)

	_, err = store.GenerateCode(ctx)
	assert.NoError(t, err)
	assert.Equal(t, 16, codesGenerated)
}
