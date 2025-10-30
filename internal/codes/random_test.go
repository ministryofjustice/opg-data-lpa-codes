package codes

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestRandomActivationCode(t *testing.T) {
	generated := randomActivationCode()
	assert.Regexp(t, `^[346789BCDFGHJKMPQRTVWXY]{12}$`, generated)

	next := randomActivationCode()
	if generated == next {
		t.Errorf("random code '%s' did not change from last '%s'", next, generated)
	}
}
