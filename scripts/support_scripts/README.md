# opg-data-lpa-codes
LPA Codes integration with UseAnLPA and Sirius: Managed by opg-org-infra &amp; Terraform

## Support scripts

The purpose of this folder is to account for various supporting scripts that we can use for ad hoc tasks
and for manual testing purposes as part of development.

### post_request.go

Makes a POST request to the codes api.

Running the script without any arguments will post a request to `v1/validate` with the `validate_payload.json` at the development api instance.

```shell
aws-vault exec identity -- go run post_request.go
```

The role, url and payload values can be supplied with flags to override the defaults.

```shell
aws-vault exec identity -- go run post_request.go \
  -role=arn:aws:iam::288342028542:role/operator \
  -url=https://dev.lpa-codes.api.opg.service.justice.gov.uk/v1/code \
  -payload=../support_files/code_payload.json
```
