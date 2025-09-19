SHELL = '/bin/bash'

build-apigw-openapi-spec:
	yq -n 'load("./lambda_functions/v1/openapi/lpa-codes-openapi-v1.yml") * load("./lambda_functions/v1/openapi/lpa-codes-openapi-aws.yml")' > ./lambda_functions/v1/openapi/lpa-codes-openapi-aws.compiled.yml

