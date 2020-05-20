import datetime
import os
import socket
import threading
import time

import boto3
import pytest
from flask import Flask

from lambda_functions.v1.functions.lpa_codes.app import create_app
from lambda_functions.v1.functions.lpa_codes.app.api import code_generator, endpoints
from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter


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


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"


@pytest.fixture(autouse=True)
def mock_db_connection(monkeypatch):
    print("I AM A FAKE DB CONNECTION")

    def not_a_real_db_connection(*args, **kwargs):
        return boto3.resource("dynamodb", endpoint_url="http://localhost:8000")

    monkeypatch.setattr(endpoints, "db_connection", not_a_real_db_connection)


@pytest.fixture()
def mock_broken_method(monkeypatch):
    return monkeypatch.setattr(code_generator, "get_codes", "this is not going to work")


@pytest.fixture(autouse=True)
def mock_get_codes(monkeypatch):
    def get_fake_codes(*args, **kwargs):
        if "key" in kwargs:
            key = kwargs["key"]
        else:
            key = {
                "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
            }
        if "code" in kwargs:
            code = kwargs["code"]
        else:
            code = "tOhkrldOqewm"

        return [
            {
                "lpa": key["lpa"],
                "actor": key["actor"],
                "code": code,
                "active": True,
                "last_updated_date": date_formatter(datetime.datetime.now()),
                "dob": None,
            }
        ]

    monkeypatch.setattr(code_generator, "get_codes", get_fake_codes)


@pytest.fixture(autouse=True)
def mock_generate_code(monkeypatch):
    def generate_predictable_code(*args, **kwargs):

        return "tOhkrldOqewm"

    monkeypatch.setattr(code_generator, "generate_code", generate_predictable_code)


@pytest.fixture(autouse=True)
def mock_update_codes(monkeypatch):
    def update_fake_codes(*args, **kwargs):

        return 0

    monkeypatch.setattr(code_generator, "update_codes", update_fake_codes)


@pytest.fixture(autouse=True)
def mock_insert_new_code(monkeypatch):
    def insert_new_fake_code(*args, **kwargs):
        key = kwargs["key"]

        return [
            {
                "lpa": key["lpa"],
                "actor": key["actor"],
                "code": "tOhkrldOqewm",
                "active": True,
                "last_updated_date": date_formatter(datetime.datetime.now()),
                "dob": None,
            }
        ]

    monkeypatch.setattr(code_generator, "insert_new_code", insert_new_fake_code)
