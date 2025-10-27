SHELL = '/bin/bash'

build-apigw-openapi-spec:
	yq -n 'load("./lambda_functions/v1/openapi/lpa-codes-openapi-v1.yml") * load("./lambda_functions/v1/openapi/lpa-codes-openapi-aws.yml")' > ./lambda_functions/v1/openapi/lpa-codes-openapi-aws.compiled.yml

up:
	docker compose up --build -d --wait --remove-orphans api-gateway

up-python:
	docker compose -f docker-compose.yml -f docker-compose.python.yml up -d lpa-codes-python

reset-database:
	@curl --fail http://localhost:8080/reset-database

test: up
	EXCLUDE_PYTHON=1 go test -count 1 .

test-both: up up-python
	go test -count 1 .

test-pact:
	docker compose run --rm --remove-orphans pact-verifier

down:
	docker compose -f docker-compose.yml -f docker-compose.python.yml down
