SHELL = '/bin/bash'

build-apigw-openapi-spec:
	yq -n 'load("./lambda_functions/v1/openapi/lpa-codes-openapi-v1.yml") * load("./lambda_functions/v1/openapi/lpa-codes-openapi-aws.yml")' > ./lambda_functions/v1/openapi/lpa-codes-openapi-aws.compiled.yml

up:
	docker compose up --build -d --wait --remove-orphans api-gateway

reset-database:
	@curl --fail http://localhost:8080/reset-database

test: up
	go test -count 1 .

test-pact:
	docker compose run --rm --remove-orphans pact-verifier

down:
	docker compose down
