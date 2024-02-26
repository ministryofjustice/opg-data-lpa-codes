# opg-data-lpa-codes

LPA Integration with microservice for the generation of registration codes: Managed by opg-org-infra &amp; Terraform

## Local Environment

To spin up the local environment run `docker-compose up -d`. From here you can either run
queries directly against the endpoint such as:

**Check healthcheck**
```
curl -X GET http://127.0.0.1:4343/v1/healthcheck
```

**Create default dynamodb table**

You must do this to be able to run the curl that calls the lambda function.

```
curl -X POST http://127.0.0.1:4343/setup/dynamodb/create/table
```

**Code generator lambda call (create example below)**
```
curl -XPOST "http://localhost:9010/2015-03-31/functions/function/invocations" -d '@./docs/support_files/lambda_request.json' | jq
```
Bear in mind that your json needs to be valid against the openapi spec and that you
may need to restart the container for your changes ot take effect. Also bear in mind
you will need to create the default table first!

You can use this thin wrapper around dynamodb that allows us to do various CRUD operations.
There is no efficient way of doing a table truncate in dynamodb so the best option is
to destroy and recreate the table.

**List all tables**
```
curl -X GET http://127.0.0.1:4343/setup/dynamodb/list
```

**Update state for pact**
```
curl -X POST -d '{"consumer": "sirius", "state": "generated code exists and active"}' -H 'Content-Type: application/json' http://localhost:4343/setup/state
```

**Create a new table from json**
```
curl -X POST -H 'Content-Type: application/json' -d '@./docs/support_files/create_table.json' http://localhost:4343/setup/dynamodb/table/test_table/create
```

**Delete a table**
```
curl -X POST http://localhost:4343/setup/dynamodb/table/test_table/delete
```

**Create new rows**
```
curl -X POST -H 'Content-Type: application/json' -d '@./docs/support_files/create_rows.json' http://localhost:4343/setup/dynamodb/table/lpa-codes-local/rows/create
```

**Get all rows**
```
curl -X GET http://localhost:4343/setup/dynamodb/table/lpa-codes-local/rows/get/all
```

**Query rows**
```
curl -X POST -H 'Content-Type: application/json' -d '{"code": "kpDHIFRahjk"}' http://localhost:4343/setup/dynamodb/table/lpa-codes-local/rows/get
```

**Delete rows**
```
curl -X POST -H 'Content-Type: application/json' -d '{"rows": [{"code": "kpDHIFRahjk"}]}' http://localhost:4343/setup/dynamodb/table/lpa-codes-local/rows/delete
```

**Delete all tables in DynamoDb (clear all)**
```
curl -X POST http://localhost:4343/setup/dynamodb/clear
```

## Unit Tests

Local unit tests use pytest and can be run locally. They use moto to mock dynamodb
so you don't need docker to be spun up to run them. You should use a virtualenv.
Check you're in root of this repo then:

```
virtualenv venv --python=python3.8
source venv/bin/activate
pip install -r ./lambda_functions/v1/requirements/dev-requirements.txt
python -m pytest
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

## PACT

To run pact locally, the easiest way to interact with it is to use the client tools.

The best package to get started can be found here:

https://github.com/pact-foundation/pact-ruby-standalone/releases/latest

You can download the latest version to a directory, unzip it and run the individual tools
in the `/pact/bin` folder from the command line or put them in your PATH.
First you should put the contract in our local broker. The local broker is spun up as part
of the `docker-compose up -d` command and you can push in a contract manually from a json file
by using the below command (example json included in this repo).

```
curl -i -X PUT -d '@./docs/support_files/sirius_contract.json' -H 'Content-Type: application/json' http://localhost:9292/pacts/provider/lpa-codes/consumer/sirius/version/x12345
```

You can then tag the consumer version so that you can run verification against the tags.
```
curl -i -X PUT -H 'Content-Type: application/json' http://localhost:9292/pacticipants/sirius/versions/x12345/tags/v1
```

Then assuming the relative path is right to pact-provider-verifier, you can verify the PACT
contract against our mock as below.

```
docker-compose run --rm pact-verifier
```

You can then see the verified results in the pact broker through your web browser. Go to:

```
http://localhost:9292/
```
