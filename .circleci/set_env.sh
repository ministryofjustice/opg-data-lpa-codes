#!/usr/bin/env bash
set -e
PACT_BROKER_USER="admin"
PACT_BROKER_BASE_URL="pact-broker.api.opg.service.justice.gov.uk"
PACT_PROVIDER="lpa-codes"
PACT_CONSUMER="sirius"
SIRIUS_GITHUB_URL="api.github.com/repos/ministryofjustice/opg-sirius"
ACCOUNT="997462338508"
ENVIRONMENT="ci"

export SECRET_STRING=$(aws sts assume-role \
--role-arn "arn:aws:iam::${ACCOUNT}:role/get-pact-secret-production" \
--role-session-name AWSCLI-Session | \
jq -r '.Credentials.SessionToken + " " + .Credentials.SecretAccessKey + " " + .Credentials.AccessKeyId')

#local export so they only exist in this stage
export AWS_ACCESS_KEY_ID=$(echo "${SECRET_STRING}" | awk -F' ' '{print $3}')
export AWS_SECRET_ACCESS_KEY=$(echo "${SECRET_STRING}" | awk -F' ' '{print $2}')
export AWS_SESSION_TOKEN=$(echo "${SECRET_STRING}" | awk -F' ' '{print $1}')

export PACT_BROKER_PASSWORD=$(aws secretsmanager get-secret-value \
--secret-id pactbroker_admin \
--region eu-west-1 | jq -r '.SecretString')

export GITHUB_STATUS_CREDENTIALS=$(aws secretsmanager get-secret-value \
--secret-id integrations_github_credentials \
--region eu-west-1 | jq -r '.SecretString')

WORKSPACE=${WORKSPACE:-$CIRCLE_BRANCH}
WORKSPACE=${WORKSPACE//[^[:alnum:]]/}
WORKSPACE=${WORKSPACE,,}
WORKSPACE=${WORKSPACE:0:14}
API_VERSION=$(ls -d lambda_functions/v*/ | awk -F'/' '{print $2}' | grep '^v[1-9]\+$' | sort -r | head -n1)
GIT_COMMIT_PROVIDER=${CIRCLE_SHA1:0:7}

echo "export GIT_COMMIT_PROVIDER=${GIT_COMMIT_PROVIDER}"
echo "export TF_WORKSPACE=${WORKSPACE}"
echo "export API_VERSION=${API_VERSION}"
echo "export PACT_PROVIDER=${PACT_PROVIDER}"
echo "export PACT_CONSUMER=${PACT_CONSUMER}"
echo "export GITHUB_STATUS_CREDENTIALS=${GITHUB_STATUS_CREDENTIALS}"
echo "export PACT_BROKER_BASE_URL=${PACT_BROKER_BASE_URL}"
echo "export PACT_BROKER_USER=${PACT_BROKER_USER}"
echo "export PACT_BROKER_PASSWORD=${PACT_BROKER_PASSWORD}"
echo "export SIRIUS_GITHUB_URL=${SIRIUS_GITHUB_URL}"
