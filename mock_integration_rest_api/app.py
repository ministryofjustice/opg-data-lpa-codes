#!/usr/bin/env python3
import boto3
import connexion
import requests
import os
from flask import Response, request, jsonify
from moto import mock_dynamodb2
from connexion.exceptions import OAuthProblem
from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import get_codes

TOKEN_DB = {"asdf1234567890": {"uid": 100}}


def apikey_auth(token, required_scopes):
    info = TOKEN_DB.get(token, None)

    if not info:
        raise OAuthProblem("Invalid token")

    return info


def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"


def mock_table():
    print("db setup")
    mock_db = boto3.resource("dynamodb")

    table = mock_db.create_table(
        TableName="lpa_codes",
        KeySchema=[{"AttributeName": "code", "KeyType": "HASH"}],  # Partition key
        AttributeDefinitions=[{"AttributeName": "code", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
    )
    key_index = [
        {
            "Create": {
                "IndexName": "key_index",
                "KeySchema": [
                    {"AttributeName": "lpa", "KeyType": "HASH"},
                    {"AttributeName": "actor", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            }
        },
    ]

    active_index = [
        {
            "Create": {
                "IndexName": "active_index",
                "KeySchema": [{"AttributeName": "active", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            }
        },
    ]

    table.update(GlobalSecondaryIndexUpdates=key_index)
    table.update(GlobalSecondaryIndexUpdates=active_index)
    return table


def tear_down_dynamo(table):
    print("db teardown")
    table.delete()


def update_dynamo(table, data):
    code = data["code"]
    lpa = data["lpa"]
    actor = data["actor"]

    key = {
        "lpa": lpa,
        "actor": actor,
    }

    table.put_item(Item=data)

    # Run test function
    result = get_codes(code=code, key=key)
    return result


def provider_states():
    mapping = {
        "generated code exists and active": setup_code_active,
        "generated code exists and not active": setup_code_not_active,
    }
    mapping[request.json["state"]]()
    return jsonify({"result": request.json["state"]})


def setup_code_active():
    table = mock_table()
    data = {
        "active": True,
        "actor": "humphrey",
        "code": "yEFJH33hn5nX",
        "expiry_date": "10/11/2020",
        "generated_date": "11/11/2019",
        "last_updated_date": "19/06/2020",
        "lpa": "streamline_distributed_content",
    }
    result = update_dynamo(table, data)
    return result, table


def setup_code_not_active():
    table = mock_table()
    data = {
        "active": False,
        "actor": "humphrey",
        "code": "hmeUqZzPniWN",
        "expiry_date": "09/08/2020",
        "generated_date": "10/08/2019",
        "last_updated_date": "08/12/2019",
        "lpa": "streamline_distributed_content",
    }
    result = update_dynamo(table, data)
    return result, table


def healthcheck():
    r = requests.get("http://127.0.0.1:5000/healthcheck")
    response = Response(r.text, status=r.status_code, mimetype="application/json")
    return response


def create():
    aws_credentials()
    with mock_dynamodb2():
        # This should be called via states endpoint
        result, table = setup_code_active()
        # Do the check, whatever that will be...
        r = requests.get("http://127.0.0.1:5000/create")
        tear_down_dynamo(table)

        response = Response(r.text, status=r.status_code, mimetype="application/json")
        print(r.text)
        return response


def validate():
    aws_credentials()
    with mock_dynamodb2():
        # This should be called via states endpoint
        result, table = setup_code_active()
        # Do the check, whatever that will be...
        r = requests.get("http://127.0.0.1:5000/validate")
        tear_down_dynamo(table)

        response = Response(r.text, status=r.status_code, mimetype="application/json")
        print(r.text)
        return response


def revoke():
    aws_credentials()
    with mock_dynamodb2():
        # This should be called via states endpoint
        result, table = setup_code_active()
        # Do the check, whatever that will be...
        r = requests.get("http://127.0.0.1:5000/revoke")
        tear_down_dynamo(table)

        response = Response(r.text, status=r.status_code, mimetype="application/json")
        print(r.text)
        return response


sirius_server = connexion.App(__name__)
sirius_server.add_api("../docs/openapi/lpa-codes-openapi-v1.yml")
sirius_server.run(port=4343)
