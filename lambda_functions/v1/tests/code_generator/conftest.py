import json

import boto3
import pytest
from moto import mock_dynamodb2
import os

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator


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


def test_data():
    return [
        {
            "active": True,
            "actor": "mediumblue",
            "code": "YsSu4iAztUXm",
            "expiry_date": "29/03/2021",
            "generated_date": "29/03/2020",
            "last_updated_date": "25/08/2020",
            "lpa": "drive_leading-edge_communities",
        },
        {
            "active": True,
            "actor": "mediumblue",
            "code": "aEYVS6i9zSwy",
            "expiry_date": "26/06/2020",
            "generated_date": "27/06/2019",
            "last_updated_date": "03/02/2020",
            "lpa": "drive_leading-edge_communities",
        },
        {
            "active": True,
            "actor": "mediumblue",
            "code": "ZY577rXcRVLY",
            "expiry_date": "05/04/2021",
            "generated_date": "05/04/2020",
            "last_updated_date": "28/02/2021",
            "lpa": "drive_leading-edge_communities",
        },
        {
            "active": False,
            "actor": "mediumblue",
            "code": "hFCarGyJF6G2",
            "expiry_date": "06/08/2020",
            "generated_date": "07/08/2019",
            "last_updated_date": "24/03/2020",
            "lpa": "drive_leading-edge_communities",
        },
        {
            "active": False,
            "actor": "mediumblue",
            "code": "hm8Qtyb763tD",
            "expiry_date": "05/08/2020",
            "generated_date": "06/08/2019",
            "last_updated_date": "01/12/2019",
            "lpa": "drive_leading-edge_communities",
        },
        {
            "active": False,
            "actor": "mediumblue",
            "code": "HiRqUNXRKB3X",
            "expiry_date": "02/01/2021",
            "generated_date": "03/01/2020",
            "last_updated_date": "11/04/2020",
            "lpa": "drive_leading-edge_communities",
        },
        {
            "active": False,
            "actor": "mediumblue",
            "code": "UEW7zSi42bLF",
            "expiry_date": "09/03/2021",
            "generated_date": "09/03/2020",
            "last_updated_date": "17/10/2020",
            "lpa": "drive_leading-edge_communities",
        },
    ]
