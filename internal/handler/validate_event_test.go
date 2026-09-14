package handler

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"testing"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
	"github.com/stretchr/testify/assert"
)

func TestValidatePublishesActivationKeyUsedEvent(t *testing.T) {
	ctx := context.Background()
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		t.Fatal(err)
	}
	cfg.BaseEndpoint = aws.String("http://localhost:8000")

	store := codes.NewActivationCodeStore(dynamodb.NewFromConfig(cfg), "lpa-codes-local")
	code := "ABCD1234EFGH" // 12 chars
	_, err = store.InsertNewCode(ctx, codes.Key{LPA: "700000000001", Actor: "700000000002"}, "1960-06-05", code)
	if err != nil {
		t.Fatal(err)
	}

	originalPublisher := ActivationKeyUsedPublisher()
	defer SetActivationKeyUsedPublisher(originalPublisher)

	called := false
	SetActivationKeyUsedPublisher(func(_ context.Context, item codes.ActivationCode) error {
		called = true
		assert.Equal(t, "700000000001", item.LPA)
		assert.Equal(t, "700000000002", item.Actor)
		return nil
	})

	resp, err := Validate(ctx, store, nil, events.APIGatewayProxyRequest{
		HTTPMethod: http.MethodPost,
		Body:       fmt.Sprintf(`{"code":"%s","lpa":"700000000001","dob":"1960-06-05"}`, code),
	})
	if !assert.NoError(t, err) {
		return
	}
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	assert.True(t, called)
	assert.JSONEq(t, `{"actor":"700000000002"}`, resp.Body)
}

func TestPublishActivationKeyUsedEventFailureIsReturned(t *testing.T) {
	originalPublisher := ActivationKeyUsedPublisher()
	defer SetActivationKeyUsedPublisher(originalPublisher)

	SetActivationKeyUsedPublisher(func(context.Context, codes.ActivationCode) error {
		return errors.New("event bridge unavailable")
	})

	err := publishActivationKeyUsed(context.Background(), codes.ActivationCode{LPA: "700000000001", Actor: "700000000002"})
	assert.Error(t, err)
	assert.EqualError(t, err, "event bridge unavailable")
}

func TestMarshalActivationKeyUsedEvent(t *testing.T) {
	payload, err := MarshalActivationKeyUsedEvent(codes.ActivationCode{LPA: "M-1234-5678-9012", Actor: "8402681d-ec7d-40da-9a5a-76e0b09cb710"})
	if !assert.NoError(t, err) {
		return
	}

	var event ActivationKeyUsedEvent
	if !assert.NoError(t, json.Unmarshal(payload, &event)) {
		return
	}

	assert.Equal(t, "M-1234-5678-9012", event.UID)
	assert.Equal(t, "8402681d-ec7d-40da-9a5a-76e0b09cb710", event.Actor)
	assert.False(t, event.UsedAt.IsZero())
}
