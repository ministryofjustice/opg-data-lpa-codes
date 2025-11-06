package codes

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestExpiryReason_MarshalUnmarshalText(t *testing.T) {
	for _, val := range []ExpiryReason{
		ExpiryReasonUnset,
		ExpiryReasonPaperToDigital,
		ExpiryReasonFirstTimeUse,
		ExpiryReasonCancelled,
	} {
		marshalled, _ := val.MarshalText()
		var unmarshalled ExpiryReason
		unmarshalled.UnmarshalText(marshalled)

		assert.Equal(t, val, unmarshalled)
	}
}

func TestExpiryReason_MarshalUnmarshalDynamoDBAttributeValue(t *testing.T) {
	for _, val := range []ExpiryReason{
		ExpiryReasonUnset,
		ExpiryReasonPaperToDigital,
		ExpiryReasonFirstTimeUse,
		ExpiryReasonCancelled,
	} {
		marshalled, _ := val.MarshalDynamoDBAttributeValue()
		var unmarshalled ExpiryReason
		unmarshalled.UnmarshalDynamoDBAttributeValue(marshalled)

		assert.Equal(t, val, unmarshalled)
	}
}
