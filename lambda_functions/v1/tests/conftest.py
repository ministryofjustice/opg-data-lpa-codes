import json

import boto3
import pytest
from flask import request
from moto import mock_dynamodb2
import os


from lambda_functions.v1.functions.lpa_codes.app.api import code_generator


@pytest.fixture(params=[True, False])
def mock_unique_code(monkeypatch, request):
    def return_unique(*args, **kwargs):
        return lambda check_result: request.param

    monkeypatch.setattr(code_generator, "check_code_unique", return_unique)


@pytest.fixture()
def mock_generate_code(monkeypatch):
    def generate_predictable_code(*args, **kwargs):
        return "idFCGZIvjess"

    monkeypatch.setattr(code_generator, "generate_code", generate_predictable_code)


@pytest.fixture()
def fake_create_data(monkeypatch):
    def create_data(*args, **kwargs):
        print("fake post data")
        data = [
            {
                "lpa": "this is my lpa",
                "actor": "this is my actor",
                "dob": "this is my dob",
            }
        ]

        return data

    monkeypatch.setattr(request, "get_json", create_data)


@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
    os.environ["ENVIRONMENT"] = "local"


@pytest.fixture(scope="session", autouse=False)
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

        yield mock_db

        print("db teardown")
        table.delete()


def insert_test_data(test_data):
    # TODO this could be a fixture
    # Set up test data
    table = boto3.resource("dynamodb").Table("lpa_codes")
    number_of_rows = len(test_data)
    for row in test_data:
        table.put_item(Item=row)

    # Check test data has been inserted as expected
    all_data = table.scan()
    before_test_data = all_data["Items"]
    assert len(before_test_data) == number_of_rows

    return before_test_data


def remove_test_data(test_data):
    # TODO this could be a fixture
    # Remove test data
    table = boto3.resource("dynamodb").Table("lpa_codes")
    for row in test_data:
        table.delete_item(Key=row)

    # Check the test data has been removed
    all_data = table.scan()
    after_tidyup_data = all_data["Items"]

    assert len(after_tidyup_data) == 0
