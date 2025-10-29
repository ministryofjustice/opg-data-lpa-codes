package codes

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestRandomAccessCode(t *testing.T) {
	generated := randomAccessCode()
	assert.Regexp(t, `^[346789BCDFGHJKMPQRTVWXY]{12}$`, generated)

	next := randomAccessCode()
	if generated == next {
		t.Errorf("random code '%s' did not change from last '%s'", next, generated)
	}
}

func TestRandomPaperVerificationCode(t *testing.T) {
	generated := randomPaperVerificationCode()
	assert.Regexp(t, `^P(-[346789BCDFGHJKMPQRTVWXY]{4}){3}-[346789BCDFGHJKMPQRTVWXY]{2}$`, generated)

	next := randomPaperVerificationCode()
	if generated == next {
		t.Errorf("random code '%s' did not change from last '%s'", next, generated)
	}
}
