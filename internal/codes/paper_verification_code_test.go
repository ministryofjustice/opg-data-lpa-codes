package codes

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestPaperVerificationCode_Code(t *testing.T) {
	assert.Equal(t, "P-1234", PaperVerificationCode{PK: paperKeyPrefix + "P-1234"}.Code())
}

func TestPaperVerification_Actor(t *testing.T) {
	assert.Equal(t, "aedcbd-e123", PaperVerificationCode{ActorLPA: "aedcbd-e123#M-1234"}.Actor())
}

func TestPaperVerificationCode_LPA(t *testing.T) {
	assert.Equal(t, "M-1234", PaperVerificationCode{ActorLPA: "aedcbd-e123#M-1234"}.LPA())
}
