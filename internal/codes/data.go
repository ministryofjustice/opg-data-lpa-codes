package codes

import (
	"strings"
	"time"
)

const paperKeyPrefix = "PAPER#"

type PaperVerificationCode struct {
	PK           string
	ActorLPA     string
	UpdatedAt    time.Time
	ExpiresAt    time.Time    `dynamodbav:",omitzero"` // omitzero not yet implemented
	ExpiryReason ExpiryReason `dynamodbav:",omitempty"`
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

type ActivationCode struct {
	Active          bool   `json:"active" dynamodbav:"active"`
	Actor           string `json:"actor" dynamodbav:"actor"`
	Code            string `json:"code" dynamodbav:"code"`
	DateOfBirth     string `json:"dob" dynamodbav:"dob"`
	ExpiryDate      int64  `json:"expiry_date" dynamodbav:"expiry_date"`
	GeneratedDate   string `json:"generated_date" dynamodbav:"generated_date"`
	LastUpdatedDate string `json:"last_updated_date" dynamodbav:"last_updated_date"`
	LPA             string `json:"lpa" dynamodbav:"lpa"`
	StatusDetails   status `json:"status_details" dynamodbav:"status_details"`
}

type Key struct {
	LPA   string
	Actor string
}

func (k Key) ToActorLPA() string {
	return k.Actor + "#" + k.LPA
}
