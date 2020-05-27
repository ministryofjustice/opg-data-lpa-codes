import os
from decimal import Decimal

import boto3
import pytest
from flask import request
from moto import mock_dynamodb2

from lambda_functions.v1.functions.lpa_codes.app.api import (
    code_generator,
    endpoints,
)
import datetime


test_constants = {
    "TABLE_NAME": "lpa-codes-mock",
    "EXPIRY_DATE": Decimal(1611216000),  # 21/01/2021 @ 8:00am (UTC)
    "EXPIRY_DATE_PAST": Decimal(1577865600),  # 01/01/2020 @ 8:00am (UTC)
    "TODAY": datetime.datetime(
        year=2020, month=1, day=21, hour=8, minute=0, second=0
    ),  # 21/01/2020 @ 8:00am (UTC)
    "TODAY_ISO": datetime.datetime(
        year=2020, month=1, day=21, hour=8, minute=0, second=0
    ).strftime(
        "%Y-%m-%d"
    ),  # 2020-01-21 @8:00am (UTC)
    "DEFAULT_CODE": "tOhkrldOqewm",
}


@pytest.fixture(autouse=True)
def mock_datetime_now(monkeypatch):
    class FakeDate(datetime.datetime):
        @classmethod
        def now(cls):
            return test_constants["TODAY"]

    monkeypatch.setattr(datetime, "datetime", FakeDate)


@pytest.fixture(autouse=True)
def mock_env_setup(monkeypatch):
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")
    monkeypatch.setenv("ENVIRONMENT", "mock")
    monkeypatch.setenv("API_VERSION", "v1")


@pytest.fixture(params=[True, False])
def mock_unique_code(monkeypatch, request):
    def return_unique(*args, **kwargs):
        return request.param

    monkeypatch.setattr(code_generator, "check_code_unique", return_unique)


@pytest.fixture()
def mock_generate_code(monkeypatch):
    def generate_predictable_code(*args, **kwargs):

        return test_constants["DEFAULT_CODE"]

    monkeypatch.setattr(code_generator, "generate_code", generate_predictable_code)


@pytest.fixture(autouse=True)
def mock_db_connection(monkeypatch):
    print("I AM A MOCK DB CONNECTION")

    def moto_db_connection(*args, **kwargs):
        return boto3.resource("dynamodb")

    monkeypatch.setattr(endpoints, "db_connection", moto_db_connection)


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


@pytest.fixture(scope="function", autouse=False)
def mock_database(aws_credentials):
    with mock_dynamodb2():
        print("db setup")
        mock_db = boto3.resource("dynamodb")
        table_name = test_constants["TABLE_NAME"]

        table = mock_db.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "code", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "code", "AttributeType": "S"},
                {"AttributeName": "lpa", "AttributeType": "S"},
                {"AttributeName": "actor", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
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
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
        )

        yield mock_db

        print("db teardown")
        table.delete()


def insert_test_data(test_data):
    # TODO this could be a fixture
    # Set up test data

    table_name = test_constants["TABLE_NAME"]
    table = boto3.resource("dynamodb").Table(table_name)
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

    table_name = test_constants["TABLE_NAME"]
    table = boto3.resource("dynamodb").Table(table_name)
    for row in test_data:
        table.delete_item(Key=row)

    # Check the test data has been removed
    all_data = table.scan()
    after_tidyup_data = all_data["Items"]

    assert len(after_tidyup_data) == 0
