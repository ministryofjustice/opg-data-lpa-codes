package codes

import (
	"strings"
	"time"
)

const paperKeyPrefix = "PAPER#"

type PaperVerificationCode struct {
	PK        string
	ActorLPA  string
	UpdatedAt time.Time
	ExpiresAt time.Time
}

func (c PaperVerificationCode) Code() string {
	return c.PK[len(paperKeyPrefix):]
}

func (c PaperVerificationCode) Actor() string {
	before, _, _ := strings.Cut(c.ActorLPA, "#")
	return before
}

func (c PaperVerificationCode) LPA() string {
	_, after, _ := strings.Cut(c.ActorLPA, "#")
	return after
}
