package main

import (
	"bytes"
	"fmt"
	"net/http"
	"time"
	"strings"
	"io/ioutil"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials/stscreds"
	"github.com/aws/aws-sdk-go/aws/session"
	v4 "github.com/aws/aws-sdk-go/aws/signer/v4"
)

func main() {

	roleToAssume := "arn:aws:iam::288342028542:role/operator"
	url := "https://in283.dev.lpa-codes.api.opg.service.justice.gov.uk/v1/validate" //change this for different endpoints
	mySession := session.Must(session.NewSession())
	creds := stscreds.NewCredentials(mySession, roleToAssume)
	cfg := aws.Config{Credentials: creds,Region: aws.String("eu-west-1")}
	sess := session.Must(session.NewSession(&cfg))
	signer := v4.NewSigner(sess.Config.Credentials)

	json, err := ioutil.ReadFile("../support_files/validate_payload.json") // just pass the file name
	if err != nil {
			fmt.Print(err)
	}
	str := string(json)

    body := strings.NewReader(str)

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
