import connexion
import boto3
import os
from flask import request, jsonify
from connexion.exceptions import OAuthProblem

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


def setup_dynamodb_table():
    aws_credentials()
    ddb = boto3.client(
        "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-west-1"
    )
    try:
        table = ddb.create_table(
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

    except ddb.exceptions.ResourceInUseException:
        print("Table already exists")


def update_state():
    aws_credentials()
    mapping = {
        "generated code exists and active": setup_code_active,
        "generated code exists and not active": setup_code_not_active,
    }
    mapping[request.json["state"]]()
    return jsonify({"result": request.json["state"]})


def setup_code_active():
    table = boto3.resource(
        "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-west-1"
    ).Table("lpa_codes")

    data = {
        "active": True,
        "actor": "humphrey",
        "code": "yEFJH33hn5nX",
        "expiry_date": "10/11/2020",
        "generated_date": "11/11/2019",
        "last_updated_date": "19/06/2020",
        "lpa": "streamline_distributed_content",
    }
    table.put_item(Item=data)
    return "Data SetUp"


def setup_code_not_active():
    table = boto3.resource(
        "dynamodb", endpoint_url="http://localhost:8000", region_name="eu-west-1"
    ).Table("lpa_codes")

    data = {
        "active": False,
        "actor": "humphrey",
        "code": "yEFJH33hn5nX",
        "expiry_date": "10/11/2020",
        "generated_date": "11/11/2019",
        "last_updated_date": "19/06/2020",
        "lpa": "streamline_distributed_content",
    }
    table.put_item(Item=data)
    return table


mock = connexion.FlaskApp(__name__, specification_dir="../../../openapi/")
mock.add_api("lpa-codes-openapi-v1.yml")
mock.add_api("state-openapi-v1.yml")
mock.run(port=4343)
