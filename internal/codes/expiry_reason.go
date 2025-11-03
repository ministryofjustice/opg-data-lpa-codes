package codes

import (
	"time"
)

type ExpiryReason uint8

const (
	ExpiryReasonUnset ExpiryReason = iota
	ExpiryReasonPaperToDigital
	ExpiryReasonFirstTimeUse
	ExpiryReasonCancelled
)

func (r ExpiryReason) String() string {
	switch r {
	case ExpiryReasonPaperToDigital:
		return "paper_to_digital"
	case ExpiryReasonFirstTimeUse:
		return "first_time_use"
	case ExpiryReasonCancelled:
		return "cancelled"
	}

	return ""
}

func (r ExpiryReason) ExpiresAt() time.Time {
	switch r {
	case ExpiryReasonPaperToDigital:
		return time.Now().AddDate(0, 0, 30)
	case ExpiryReasonFirstTimeUse:
		return time.Now().AddDate(2, 0, 0)
	case ExpiryReasonCancelled:
		return time.Now()
	}

	return time.Time{}
}

func (r ExpiryReason) MarshalText() ([]byte, error) {
	return []byte(r.String()), nil
}

func (r *ExpiryReason) UnmarshalText(text []byte) error {
	switch string(text) {
	case "paper_to_digital":
		*r = ExpiryReasonPaperToDigital
	case "first_time_use":
		*r = ExpiryReasonFirstTimeUse
	case "cancelled":
		*r = ExpiryReasonCancelled
	default:
		*r = ExpiryReasonUnset
	}

	return nil
}
