SHELL = '/bin/bash'

build-apigw-openapi-spec:
	yq -n 'load("./lambda_functions/v1/openapi/lpa-codes-openapi-v1.yml") * load("./lambda_functions/v1/openapi/lpa-codes-openapi-aws.yml")' > ./lambda_functions/v1/openapi/lpa-codes-openapi-aws.compiled.yml

up: pact-down
	docker compose up --build -d --wait lpa-codes-go

test: up
	EXCLUDE_PYTHON=1 go test -count 1 .

down:
	docker compose down

pact-up: down
	docker compose -f docker-compose-pact.yml up -d --build --wait api_gateway-go

pact-test: pact-up
	docker compose -f docker-compose-pact.yml run --rm pact-verifier

pact-down:
	docker compose -f docker-compose-pact.yml down
