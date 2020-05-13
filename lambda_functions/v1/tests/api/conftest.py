import threading
import socket
import time

import boto3
import pytest
import os

from flask import Flask
from moto import mock_dynamodb2

from lambda_functions.v1.functions.lpa_codes.app import create_app


def get_open_port():
    """ Find free port on a local system """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def wait_until(predicate, timeout=5, interval=0.05, *args, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if predicate(*args, **kwargs):
            return True
        time.sleep(interval)
    return False


@pytest.fixture
def server():
    http_server = create_app(Flask)

    # os.environ['FLASK_DEBUG'] = '1'
    # os.environ['FLASK_ENV'] = 'development'
    os.environ["LOGGER_LEVEL"] = "DEBUG"

    port = get_open_port()
    http_server.url = "http://localhost:{}".format(port)

    def start():
        print("start server")
        http_server.run(port=port)

    p = threading.Thread(target=start)
    p.daemon = True
    p.start()

    def check():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("localhost", port))
            return True
        except Exception:
            return False
        finally:
            s.close()

    rc = wait_until(check)
    assert rc, "failed to start service"

    yield http_server

    p.join(timeout=0.5)


# @pytest.fixture(autouse=True)
# def mock_env_setup(monkeypatch):
#     monkeypatch.setenv("DYNAMODB_URL", "http://localhost:8000")


@pytest.fixture(autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
    os.environ["DYNAMODB_URL"] = "http://localhost:8000"


@pytest.fixture(scope="function", autouse=True)
def create_database(aws_credentials):

    print(f"local db setup on {os.environ['DYNAMODB_URL']}")
    local_dynamodb = boto3.resource("dynamodb", endpoint_url=os.environ["DYNAMODB_URL"])

    try:
        table = local_dynamodb.Table("lpa_codes")
        table.delete()
    except Exception:
        pass

    table = local_dynamodb.create_table(
        TableName="lpa_codes",
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

    default_test_data = [
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

    for row in default_test_data:
        table.put_item(Item=row)

    yield local_dynamodb

    # print("db teardown")
    # table.delete()
