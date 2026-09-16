package handler

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/ministryofjustice/opg-data-lpa-codes/internal/codes"
)

// ActivationKeyUsedEvent matches the schema at
// https://ministryofjustice.github.io/opg-event-store/domains/POAS/events/activation-key-used/
type ActivationKeyUsedEvent struct {
	UID    string    `json:"uid"`
	Actor  string    `json:"actor"`
	UsedAt time.Time `json:"usedAt"`
}

type activationKeyUsedPublisher func(context.Context, codes.ActivationCode) error

var activationKeyUsedPublisherFunc activationKeyUsedPublisher = func(context.Context, codes.ActivationCode) error {
	return nil
}

func ActivationKeyUsedPublisher() func(context.Context, codes.ActivationCode) error {
	return activationKeyUsedPublisherFunc
}

func SetActivationKeyUsedPublisher(fn func(context.Context, codes.ActivationCode) error) {
	if fn == nil {
		activationKeyUsedPublisherFunc = func(context.Context, codes.ActivationCode) error { return nil }
		return
	}

	activationKeyUsedPublisherFunc = fn
}

func publishActivationKeyUsed(ctx context.Context, item codes.ActivationCode) error {
	if activationKeyUsedPublisherFunc == nil {
		return nil
	}

	return activationKeyUsedPublisherFunc(ctx, item)
}

func NewActivationKeyUsedEvent(item codes.ActivationCode) ActivationKeyUsedEvent {
	return ActivationKeyUsedEvent{
		UID:    item.LPA,
		Actor:  item.Actor,
		UsedAt: time.Now().UTC(),
	}
}

func MarshalActivationKeyUsedEvent(item codes.ActivationCode) ([]byte, error) {
	return json.Marshal(NewActivationKeyUsedEvent(item))
}

func EventBridgeError(errCode, errMessage *string) error {
	if errCode != nil && errMessage != nil {
		return fmt.Errorf("eventbridge put events failed: %s: %s", *errCode, *errMessage)
	}
	if errCode != nil {
		return fmt.Errorf("eventbridge put events failed: %s", *errCode)
	}
	if errMessage != nil {
		return fmt.Errorf("eventbridge put events failed: %s", *errMessage)
	}
	return fmt.Errorf("eventbridge put events failed")
}
