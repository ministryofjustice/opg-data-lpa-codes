#!/usr/bin/env bash
set -e
PACT_BROKER_USER="admin"
PACT_BROKER_BASE_URL="https://pact-broker.api.opg.service.justice.gov.uk"
PACT_PROVIDER="data-lpa-codes"
PACT_CONSUMER="sirius"
SIRIUS_GITHUB_URL="api.github.com/repos/ministryofjustice/opg-sirius"
ACCOUNT="997462338508"
ENVIRONMENT="ci"

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
echo "export SIRIUS_GITHUB_URL=${SIRIUS_GITHUB_URL}"
echo "export ENVIRONMENT=${ENVIRONMENT}"
