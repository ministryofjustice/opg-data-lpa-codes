#!/usr/bin/env bash
set -e
if [ "${CONSUMER_TRIGGERED}" == "false" ]
then
    echo "Validating against consumer tag ${API_VERSION}"
    #  Verify current provider git_commit against latest consumer git_commit tagged with v<x>
    ./pact/bin/pact-provider-verifier --provider-base-url=http://localhost:4343/"${API_VERSION}" \
    --custom-provider-header 'Authorization: asdf1234567890' \
    --pact-broker-base-url="https://${PACT_BROKER_BASE_URL}" \
    --provider="lpa-codes" \
    --broker-username="${PACT_BROKER_USER}" \
    --broker-password="${PACT_BROKER_PASSWORD}" -r \
    --consumer-version-tag="${API_VERSION}" \
    --provider-version-tag="${API_VERSION}" \
    --provider-app-version="${GIT_COMMIT_PROVIDER}" || echo "Error validating, didn't validate"

    echo "Validating against consumer tag ${API_VERSION}_production"
    # Verify current provider git_commit against latest consumer git_commit tagged with v<x>_production
    ./pact/bin/pact-provider-verifier --provider-base-url=http://localhost:4343/"${API_VERSION}" \
    --custom-provider-header 'Authorization: asdf1234567890' \
    --pact-broker-base-url="https://${PACT_BROKER_BASE_URL}" \
    --provider="lpa-codes" \
    --broker-username="${PACT_BROKER_USER}" \
    --broker-password="${PACT_BROKER_PASSWORD}" -r \
    --consumer-version-tag="${API_VERSION}_production" \
    --provider-version-tag="${API_VERSION}" \
    --provider-app-version="${GIT_COMMIT_PROVIDER}" || echo "Error validating, didn't validate"
elif [ "${CONSUMER_TRIGGERED}" == "true" ]
then
  printf "\n\nConsumer verification not done here. See check_pact_deployable.sh\n\n"
else
  echo "Error! Environment variable CONSUMER_TRIGGERED must be set to true or false"
  exit 1
fi
