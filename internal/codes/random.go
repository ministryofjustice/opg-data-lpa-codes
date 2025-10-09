package codes

import "crypto/rand"

const codeSize = 12
const codeCharset = "346789BCDFGHJKMPQRTVWXY"

func randomCode() string {
	bytes := make([]byte, codeSize)
	_, err := rand.Read(bytes)
	if err != nil {
		panic(err)
	}
	for i, b := range bytes {
		bytes[i] = codeCharset[b%byte(len(codeCharset))]
	}
	return string(bytes)
}
