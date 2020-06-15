#!/usr/bin/env bash
set -e
if [ "${CONSUMER_TRIGGERED}" == "false" ]
then
    # Canideploy with provider git_commit against latest consumer tagged with v<x>_production
    CANIDEPLOY_RESPONSE=$(./pact/bin/pact-broker can-i-deploy \
    --broker-base-url="https://${PACT_BROKER_BASE_URL}" \
    --broker-username="${PACT_BROKER_USER}" \
    --broker-password="${PACT_BROKER_PASSWORD}" \
    --pacticipant="sirius" \
    --latest "${API_VERSION}_production" \
    --pacticipant "lpa-codes" \
    --version "${GIT_COMMIT_PROVIDER}" \
    | tail -1)

    # If the prod version doesn't exist then it's a breaking change or a new version
    # we are allowed to try the dev version
    if [ "$(echo "${CANIDEPLOY_RESPONSE}" \
        | grep -c "No version with tag ${API_VERSION}_production exists for sirius")" -ne 0 ]
    then
        # Canideploy with provider git_commit against latest consumer tagged with v<x>
        CANIDEPLOY_RESPONSE=$(./pact/bin/pact-broker can-i-deploy \
        --broker-base-url="https://${PACT_BROKER_BASE_URL}" \
        --broker-username="${PACT_BROKER_USER}" \
        --broker-password="${PACT_BROKER_PASSWORD}" \
        --pacticipant="sirius" \
        --latest "${API_VERSION}" \
        --pacticipant "lpa-codes" \
        --version "${GIT_COMMIT_PROVIDER}" \
        | tail -1)
    fi

    if [ "$(echo "${CANIDEPLOY_RESPONSE}" \
        | grep -c "No version with tag ${API_VERSION} exists for sirius")" -ne 0 ]
    then
        echo "Provider Side 'Can I Deploy' Failed! No matching consumer pact!"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY="false"
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "No pacts or verifications have been published")" -ne 0 ]
    then
        echo "Provider Side 'Can I Deploy' Failed! No pacts or verifications published!"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY="false"
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "failed")" -ne 0 ]
    then
        echo "Provider Side 'Can I Deploy' Failed!"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY="false"
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "successful")" -ne 0 ]
    then
        echo "Provider Side 'Can I Deploy' Successful"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY="true"
    fi

    if [ "${CAN_I_DEPLOY}" == "false" ]
    then
        echo "Failing the build"
        exit
    fi

elif [ "${CONSUMER_TRIGGERED}" == "true" ]
then

    # Get the API version from the tag associated with consumer commit
    CONSUMER_API_VERSION=$(curl -s -u "${PACT_BROKER_USER}":"${PACT_BROKER_PASSWORD}" \
    -X GET https://"${PACT_BROKER_BASE_URL}"/pacticipants/"${PACT_CONSUMER}"/versions/"${GIT_COMMIT_CONSUMER}" \
    | jq ._embedded.tags[] | jq .name | sed 's/"//g' | grep '^v[1-9]\+\|^v[1-9]\+_production$' \
    | awk -F'_' '{print $1}' | sort -r | head -n1)
    echo "The consumer version we are testing is ${CONSUMER_API_VERSION}"

    # Get the full commit sha for later use
    export CONSUMER_FULL_COMMIT_SHA=$(curl -s -u "${GITHUB_STATUS_CREDENTIALS}" \
    -X GET https://"${GITHUB_SIRIUS_GITHUB_URL}"/commits/"${GIT_COMMIT_CONSUMER}" | jq -r .sha) >> /dev/null

    # CanIDeploy with consumer git_commit and latest provider tagged with v<x>_production (must get version from tags)
    CANIDEPLOY_RESPONSE=$(./pact/bin/pact-broker can-i-deploy \
    --broker-base-url "https://${PACT_BROKER_BASE_URL}" \
    --broker-username="${PACT_BROKER_USER}" \
    --broker-password="${PACT_BROKER_PASSWORD}" \
    --pacticipant "sirius" \
    --version "${GIT_COMMIT_CONSUMER}" \
    --pacticipant "lpa-codes" \
    --latest "${CONSUMER_API_VERSION}_production" \
    | tail -1)

    if [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "There is no verified pact")" -ne 0 ]
    then
        echo "Running verification as this is a new pact!"
        # New Pact has not been verified before. We must verify it!
        # Verify this commit against what is in master using this providers GIT_SHA
        # Tag provider with latest version tag (this may be different to what version is being passed from sirius)
        # This is intended as we only want to allow changes that will work against the 'live' provider
        # There is an issue that what we're comparing against may be in master but not prod but it's a fringe case
        ./pact/bin/pact-provider-verifier --provider-base-url=http://localhost:4343/"${API_VERSION}" \
        --custom-provider-header 'Authorization: asdf1234567890' \
        --pact-broker-base-url="https://${PACT_BROKER_BASE_URL}" \
        --provider="lpa-codes" \
        --broker-username="${PACT_BROKER_USER}" \
        --broker-password="${PACT_BROKER_PASSWORD}" -r \
        --consumer-version-tag="${API_VERSION}" \
        --provider-app-version="${GIT_COMMIT_PROVIDER}" || echo "Error validating, didn't validate"
        # Rerun can I deploy
        echo "Rerunning canideploy"
        CANIDEPLOY_RESPONSE=$(./pact/bin/pact-broker can-i-deploy \
        --broker-base-url "https://${PACT_BROKER_BASE_URL}" \
        --broker-username="${PACT_BROKER_USER}" \
        --broker-password="${PACT_BROKER_PASSWORD}" \
        --pacticipant "sirius" \
        --version "${GIT_COMMIT_CONSUMER}" \
        --pacticipant "lpa-codes" \
        --latest "${CONSUMER_API_VERSION}_production" \
        | tail -1)
    fi

    if [ "$(echo "${CANIDEPLOY_RESPONSE}" \
        | grep -c "No version with tag ${CONSUMER_API_VERSION} exists for lpa-codes")" -ne 0 ]
    then
        echo "Consumer Side 'Can I Deploy' Failed! No matching provider pact with that tag!"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY="false"
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" \
    | grep -c "No version with tag ${CONSUMER_API_VERSION}_production exists for lpa-codes")" -ne 0 ]
    then
        echo "Consumer Side 'Can I Deploy' Failed! No matching provider pact with that tag!"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY="false"
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "failed")" -ne 0 ]
    then
        echo "Consumer Side 'Can I Deploy' Failed!"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY="false"
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "successful")" -ne 0 ]
    then
        echo "Consumer Side 'Can I Deploy' Successful"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY="true"
    fi
    # Send status update to sirius
    if [ "${CONSUMER_FULL_COMMIT_SHA}" != "" ]
    then
      if [ "${CAN_I_DEPLOY}" == "true" ]
      then
          echo "Github Status Updated - Verification Successful"
          curl -X POST \
          -H "Content-Type: application/json" \
          -u "${GITHUB_STATUS_CREDENTIALS}" \
          -d '{"state":"success","target_url":"https://'"${PACT_BROKER_BASE_URL}"'/","description":"Our build was verified!","context":"pactbroker"}' \
          https://"${GITHUB_SIRIUS_GITHUB_URL}"/statuses/"${CONSUMER_FULL_COMMIT_SHA}"
      elif [ "${CAN_I_DEPLOY}" == "false" ]
      then
          echo "Github Status Updated - Verification Failed"
          curl -X POST \
          -H "Content-Type: application/json" \
          -u "${GITHUB_STATUS_CREDENTIALS}" \
          -d '{"state":"failure","target_url":"https://'"${PACT_BROKER_BASE_URL}"'/","description":"Our build failed verification!","context":"pactbroker"}' \
          https://"${GITHUB_SIRIUS_GITHUB_URL}"/statuses/"${CONSUMER_FULL_COMMIT_SHA}"
      else
          echo "CAN_I_DEPLOY not set"
      fi
    else
      echo "No value set for CONSUMER_FULL_COMMIT_SHA. Check user has access to repo"
    fi
else
    echo "Environment variable, CONSUMER_TRIGGERED not set"
    exit 1
fi
