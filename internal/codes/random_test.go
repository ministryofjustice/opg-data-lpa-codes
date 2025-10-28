package codes

import (
	"regexp"
	"testing"
)

func TestRandomAccessCode(t *testing.T) {
	generated := randomAccessCode()
	if ok, _ := regexp.MatchString(`^[346789BCDFGHJKMPQRTVWXY]{12}$`, generated); !ok {
		t.Errorf("random code '%s' did not match expected pattern", generated)
	}

	next := randomAccessCode()
	if generated == next {
		t.Errorf("random code '%s' did not change from last '%s'", next, generated)
	}
}

func TestRandomPaperVerificationCode(t *testing.T) {
	generated := randomPaperVerificationCode()
	if ok, _ := regexp.MatchString(`^P(-[346789BCDFGHJKMPQRTVWXY]{4}){3}-[346789BCDFGHJKMPQRTVWXY]{2}$`, generated); !ok {
		t.Errorf("random code '%s' did not match expected pattern", generated)
	}

	next := randomPaperVerificationCode()
	if generated == next {
		t.Errorf("random code '%s' did not change from last '%s'", next, generated)
	}
}
