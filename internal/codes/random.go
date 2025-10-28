package codes

import (
	"crypto/rand"
	"math/big"
)

const (
	accessCodeSize            = 12                        // unformatted
	paperVerificationCodeSize = 19                        // formatted
	codeCharset               = "346789BCDFGHJKMPQRTVWXY" // pragma: allowlist secret
	codeCharsetLength         = int64(len(codeCharset))
)

func randomAccessCode() string {
	out := make([]byte, accessCodeSize)
	maxInt := big.NewInt(codeCharsetLength)

	for i := range accessCodeSize {
		n, _ := rand.Int(rand.Reader, maxInt)
		out[i] = codeCharset[n.Int64()%codeCharsetLength]
	}

	return string(out)
}

func randomPaperVerificationCode() string {
	out := make([]byte, paperVerificationCodeSize)
	maxInt := big.NewInt(codeCharsetLength)

	for i := range paperVerificationCodeSize {
		switch i {
		case 0:
			out[i] = 'P'
		case 1, 6, 11, 16:
			out[i] = '-'
		default:
			n, _ := rand.Int(rand.Reader, maxInt)
			out[i] = codeCharset[n.Int64()%codeCharsetLength]
		}
	}

	return string(out)
}
