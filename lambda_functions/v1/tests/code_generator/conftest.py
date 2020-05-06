import json

import boto3
import pytest
from moto import mock_dynamodb2

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.tests.code_generator.test_data import test_data


@pytest.fixture()
def mock_unique_code(monkeypatch):
    def unique_true(*args, **kwargs):
        return False

    monkeypatch.setattr(code_generator, "check_code_unique", unique_true)


@pytest.fixture(scope="session", autouse=False)
def mock_database():
    with mock_dynamodb2():
        print("db setup")
        mock_db = boto3.resource("dynamodb")

        table = mock_db.create_table(
            TableName="lpa_codes",
            KeySchema=[
                {"AttributeName": "lpa", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "actor", "KeyType": "RANGE"},  # Sort key
                {"AttributeName": "code", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "lpa", "AttributeType": "S"},
                {"AttributeName": "actor", "AttributeType": "S"},
                {"AttributeName": "code", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
        )

        code_index = [
            {
                "Create": {
                    "IndexName": "code_index",
                    "KeySchema": [{"AttributeName": "code", "KeyType": "HASH"}],
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

        table.update(GlobalSecondaryIndexUpdates=code_index)
        table.update(GlobalSecondaryIndexUpdates=active_index)

        data = test_data()
        for row in data:
            table.put_item(Item=row)

        yield mock_db

        print("db teardown")
        table.delete()
