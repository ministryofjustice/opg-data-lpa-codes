package main

import (
	"bytes"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials/stscreds"
	"github.com/aws/aws-sdk-go/aws/session"
	v4 "github.com/aws/aws-sdk-go/aws/signer/v4"
)

func main() {
	flag.Usage = func() {
		fmt.Println("Usage: Send request to API. flags accepted for role, url and payload.")
		flag.PrintDefaults()
	}

	// gather imputs or use defaults
	var roleToAssume string
	var url string
	var inputPayload string
	flag.StringVar(&roleToAssume, "role", "arn:aws:iam::288342028542:role/operator", "Role to assume when signing requests for API")
	flag.StringVar(&url, "url", "https://dev.lpa-codes.api.opg.service.justice.gov.uk/v1/validate", "url including version and endpoint of API to send request to")
	flag.StringVar(&inputPayload, "payload", "../support_files/validate_payload.json", "path to payload for request")
	flag.Parse()
	fmt.Println(roleToAssume, url, inputPayload)

	// use credentials to create a signer
	mySession := session.Must(session.NewSession())
	creds := stscreds.NewCredentials(mySession, roleToAssume)
	cfg := aws.Config{Credentials: creds, Region: aws.String("eu-west-1")}
	sess := session.Must(session.NewSession(&cfg))
	signer := v4.NewSigner(sess.Config.Credentials)

	// create body for request
	json, err := ioutil.ReadFile(inputPayload)
	if err != nil {
		fmt.Print(err)
	}
	str := string(json)

	body := strings.NewReader(str)

	//create a request
	req, _ := http.NewRequest(http.MethodPost, url, body)
	req.Header.Set("Content-Type", "application/json")

	_, err = signer.Sign(req, body, "execute-api", *cfg.Region, time.Now())
	if err != nil {
		fmt.Printf("failed to sign request: (%v)\n", err)
	}

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		fmt.Printf("failed to call remote service: (%v)\n", err)
	}

	defer res.Body.Close()
	if res.StatusCode != 200 {
		fmt.Printf("ERROR: (%d): (%s)\n", res.StatusCode, res.Status)
	}

	buf := new(bytes.Buffer)
	buf.ReadFrom(res.Body)
	newStr := buf.String()
	fmt.Println(res.StatusCode)
	fmt.Println(res.Status)
	fmt.Println(newStr)
}
