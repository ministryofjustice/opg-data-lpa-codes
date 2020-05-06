import json

import boto3
import pytest
from moto import mock_dynamodb2
import os

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.tests.code_generator.test_data import test_data

# from lambda_functions.v1.tests.code_generator.test_data import test_data


@pytest.fixture()
def mock_unique_code(monkeypatch):
    def unique_true(*args, **kwargs):
        return False

    monkeypatch.setattr(code_generator, "check_code_unique", unique_true)


@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"


@pytest.fixture(scope="function", autouse=False)
def mock_database(aws_credentials):
    with mock_dynamodb2():
        print("db setup")
        mock_db = boto3.resource("dynamodb")

        table = mock_db.create_table(
            TableName="lpa_codes",
            KeySchema=[
                {"AttributeName": "code", "KeyType": "HASH"},  # Partition key
                # {"AttributeName": "lpa", "KeyType": "RANGE"},  # Sort key
                # {"AttributeName": "actor", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "code", "AttributeType": "S"},
                # {"AttributeName": "lpa", "AttributeType": "S"},
                # {"AttributeName": "actor", "AttributeType": "S"},
            ],
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

        data = test_data()
        for row in data:
            table.put_item(Item=row)

        yield mock_db

        print("db teardown")
        table.delete()
