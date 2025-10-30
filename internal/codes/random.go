package codes

import (
	"crypto/rand"
	"math/big"
)

const (
	activationCodeSize = 12
	codeCharset        = "346789BCDFGHJKMPQRTVWXY" // pragma: allowlist secret
	codeCharsetLength  = int64(len(codeCharset))
)

func randomActivationCode() string {
	out := make([]byte, activationCodeSize)
	maxInt := big.NewInt(codeCharsetLength)

	for i := range activationCodeSize {
		n, _ := rand.Int(rand.Reader, maxInt)
		out[i] = codeCharset[n.Int64()%codeCharsetLength]
	}

	return string(out)
}
