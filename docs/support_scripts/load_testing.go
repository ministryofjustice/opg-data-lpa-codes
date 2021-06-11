package main

import (
	js "encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials/stscreds"
	"github.com/aws/aws-sdk-go/aws/session"
	v4 "github.com/aws/aws-sdk-go/aws/signer/v4"
)

//Struct for creating codes
type Lpa struct{
	Lpa   string `json:"lpa"`
	Actor string `json:"actor"`
	Dob   string `json:"dob"`
} 

type CodeCreate struct {
	Lpas []Lpa `json:"lpas"`
}

//Struct and variable for responses from code creation
type Codes struct {
	Codes []struct {
		Actor string `json:"actor"`
		Code  string `json:"code"`
		Lpa   string `json:"lpa"`
	} `json:"codes"`
}

var code Codes

//Struct for validation of codes
type CodeValidate struct {
	Lpa string `json:"lpa"`
	Dob string `json:"dob"`
	Code string `json:"code"`
}

//Struct for revocation of codes
type CodeRevoke struct {
	Code string `json:"code"`
}

func makeRequest(url string, ch chan<-string, chCode chan<-string, chStatus chan<-int, signer *v4.Signer, cfg aws.Config, payload *strings.Reader) {
  start := time.Now()

	req, _ := http.NewRequest(http.MethodPost, url, payload)
	req.Header.Set("Content-Type", "application/json")

	_, err := signer.Sign(req, payload, "execute-api", *cfg.Region, time.Now())
	if err != nil {
		fmt.Printf("failed to sign request: (%v)\n", err)
	}
	
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		fmt.Printf("failed to call remote service: (%v)\n", err)
	}

	defer res.Body.Close()
	
	secs := time.Since(start).Seconds()
	
	respbody, _ := ioutil.ReadAll(res.Body)
	
	ch <- fmt.Sprintf("%.2f elapsed with response length: %d Status: %d StartTime: %v", secs, len(respbody), res.StatusCode, time.Time(start))
	chCode <- string(respbody)
	chStatus <- res.StatusCode
	
}

func makeRequests (baseUrl string, endpoint string, codesToAction []*strings.Reader, 
	ch chan string, chCode chan string, chStatus chan int, signer *v4.Signer, cfg aws.Config) []string {
	url := baseUrl + "/" + endpoint
	start := time.Now()
	for _,body := range codesToAction {
		go makeRequest(url, ch, chCode, chStatus, signer, cfg, body)
	}

	var listOfAction []string
	var listOfActionResponses []string
	okCount := 0
	failCount := 0
	for range codesToAction {
		listOfActionResponses = append(listOfActionResponses, <-ch)
		listOfAction = append(listOfAction, <-chCode)
		if <-chStatus <= 399 {
			okCount++
		} else {
			failCount++
		}
	}	
	fmt.Printf("Running %v requests\n", endpoint)
	fmt.Printf("Run finished in %.2fs\n", time.Since(start).Seconds())
	fmt.Printf("%v requests successful, %v requests failed.\n\n\n", okCount, failCount)
	
	return listOfAction
}

func main() {

	roleToAssume := "arn:aws:iam::288342028542:role/operator"
	baseUrl := "https://in673.dev.lpa-codes.api.opg.service.justice.gov.uk/v1"
	
	mySession := session.Must(session.NewSession())
	creds := stscreds.NewCredentials(mySession, roleToAssume)
	cfg := aws.Config{Credentials: creds,Region: aws.String("eu-west-1")}
	sess := session.Must(session.NewSession(&cfg))
	signer := v4.NewSigner(sess.Config.Credentials)

	var listOfCreate []*strings.Reader

	var ref int
	var countCodesToUse int

	countCodesToUse = 10
	ref = 700000000000
	
	fmt.Printf("\n===== Starting Load Test With %v Codes To Create, Validate and Revoke =====\n\n", countCodesToUse)

	for i := 0; i < countCodesToUse; i++ {
		
		ref++
		reference := strconv.FormatInt(int64(ref), 10)
		
		lpa := Lpa{
			Lpa: reference,
			Actor: reference, 
			Dob: "1960-06-05", 
		}
	
		postanlpa := CodeCreate{
			[]Lpa{
				lpa,
			},
		}
	
		var jsonData []byte
		jsonData, err := js.Marshal(postanlpa)
		if err != nil {
			fmt.Print(err)
		}
		strJsonData := string(jsonData)
		body := strings.NewReader(strJsonData)
		
		listOfCreate=append(listOfCreate, body)	

	}

	ch := make(chan string)
	chCode := make(chan string)
	chStatus := make(chan int)
	listOfCodes := makeRequests (baseUrl, "create", listOfCreate, ch, chCode, chStatus, signer, cfg)

	//Codes to validate section
	var codesToValidate []*strings.Reader

	for _,jsonCode := range listOfCodes {

		err := js.Unmarshal([]byte(jsonCode), &code)
		if err != nil {
			fmt.Print(err)
		}

		lpaValidate := CodeValidate{
			Lpa: code.Codes[0].Lpa,
			Dob: "1960-06-05", 
			Code: code.Codes[0].Code, 
		}
	
		var jsonData []byte
		jsonData, err = js.Marshal(lpaValidate)
		if err != nil {
			fmt.Print(err)
		}
		strJsonData := string(jsonData)
		body := strings.NewReader(strJsonData)

		codesToValidate = append(codesToValidate, body)
	
	}

	makeRequests (baseUrl, "validate", codesToValidate, ch, chCode, chStatus, signer, cfg)

	//Codes to revoke section
	var codesToRevoke []*strings.Reader

	for _,jsonCode := range listOfCodes {

		err := js.Unmarshal([]byte(jsonCode), &code)
		if err != nil {
			fmt.Print(err)
		}

		lpaRevoke := CodeRevoke{
			Code: code.Codes[0].Code, 
		}
	
		var jsonData []byte
		jsonData, err = js.Marshal(lpaRevoke)
		if err != nil {
			fmt.Print(err)
		}
		strJsonData := string(jsonData)
		body := strings.NewReader(strJsonData)

		codesToRevoke = append(codesToRevoke, body)
	}

	makeRequests (baseUrl, "revoke", codesToRevoke, ch, chCode, chStatus, signer, cfg)
	
}
