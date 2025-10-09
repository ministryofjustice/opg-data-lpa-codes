# opg-data-lpa-codes

LPA Integration with microservice for the generation of registration codes: Managed by opg-org-infra &amp; Terraform


## Development

Tests are written in `main_test.go`. To run them use:

```
make test
```

Once the tests have been run you'll be able to call the Lambda using this example request:

```
curl -XPOST "http://localhost:9010/2015-03-31/functions/function/invocations" -d '@./docs/support_files/lambda_request.json' | jq
```

The current pacts can be verified by running:

```
make pact-test
```

With this (or `make pact-up`) a mock API Gateway is created, this allows you to make local requests easier, for example:

```
curl http://localhost:4444/v1/healthcheck
curl http://localhost:4444/v1/create -XPOST -d @./docs/support_files/create_payload.json
```

## CI Pipeline

When working on a ticket you should name your branch with the jira identifier of the ticket you are working on.

When you push your changes to your branch and create a PR then the Github action will run and create a branch
based environment in aws. This includes an api gateway instance, the lambda function and all the relevant DNS to access
the environment.

You can test against the endpoints by assuming a sirius dev role and hitting the following endpoint (replacing branch_name and api_path:

```
https://branch_name.dev.lpa-codes.api.opg.service.justice.gov.uk/v1/api_path
```

Once merged you can do the same tests against dev by removing the branch_name portion of above url.

Environments get destroyed overnight and by default your environment is protected for the first night's destroy but
will be cleaned up on the subsequent night. If you want to work on it longer either recreate it by rerunning the workflow
or  change the protection TTL in dynamodb.
