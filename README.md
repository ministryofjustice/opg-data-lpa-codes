# opg-data-lpa-codes
LPA Integration with microservice for the generation of registration codes: Managed by opg-org-infra &amp; Terraform

## Local Environment

To spin up the local environment run `docker-compose up -d`. From here you can either run
queries directly against the endpoint such as:

**Check healthcheck**
```
curl -X GET http://127.0.0.1:4343/v1/healthcheck
```

**Code generator operation (create example below)**
```
curl -X POST -H 'Content-Type: application/json' -H 'Authorization: asdf1234567890' -d '@./docs/support_files/create_payload.json' http://localhost:4343/v1/create
```

Bear in mind that your json needs to be valid against the openapi spec and that you
may need to restart the container for your changes ot take effect. Also bear in mind
you will need to create the default table first (command below)!!

You can use this thin wrapper around dynamodb that allows us to do various CRUD operations.
There is no efficient way of doing a table truncate in dynamodb so the best option is
to destroy and recreate the table.

**Create default dynamodb table**
```
curl -X POST http://127.0.0.1:4343/setup/dynamodb/create/table
```

**List all tables**
```
curl -X POST http://127.0.0.1:4343/setup/dynamodb/list
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
curl -X POST -H 'Content-Type: application/json' -d '@./docs/support_files/create_rows.json' http://localhost:4343/setup/dynamodb/table/lpa_codes/rows/create
```

**Get all rows**
```
curl -X GET http://localhost:4343/setup/dynamodb/table/lpa_codes/rows/get/all
```

**Query rows**
```
curl -X POST -H 'Content-Type: application/json' -d '{"code": "kpDHIFRahjk"}' http://localhost:4343/setup/dynamodb/table/lpa_codes/rows/get
```

**Delete rows**
```
curl -X POST -H 'Content-Type: application/json' -d '{"rows": [{"code": "kpDHIFRahjk"}]}' http://localhost:4343/setup/dynamodb/table/lpa_codes/rows/delete
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
virtualenv venv
source venv/bin/activate
pip install -r ./lambda_functions/v1/requirements/dev-requirements.txt
python -m pytest
```
