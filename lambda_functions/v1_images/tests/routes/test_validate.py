import json

import requests

import pytest

response_400 = {
    "body": {"error": {"code": "Bad Request", "message": "Bad payload"}},
    "headers": {"Content-Type": "application/json"},
    "isBase64Encoded": False,
    "statusCode": 400,
}


@pytest.mark.run(order=1)
def test_validate(server):

    with server.app_context():
        test_data = {
            "code": "hdgeytkvnshd",
            "lpa": "eed4f597-fd87-4536-99d0-895778824861",
            "dob": "1960-06-05",
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = {"actor": None}

        r = requests.post(
            server.url + "/validate", headers=test_headers, data=json.dumps(test_data)
        )

        assert r.status_code == 200
        assert r.json() == expected_return


@pytest.mark.run(order=1)
def test_validate_missing_code(server):

    with server.app_context():
        test_data = {
            # "code": "hdgeytkvnshd",
            "lpa": "eed4f597-fd87-4536-99d0-895778824861",
            "dob": "1960-06-05",
        }

        test_headers = {"Content-Type": "application/json"}

        r = requests.post(
            server.url + "/validate", headers=test_headers, data=json.dumps(test_data)
        )

        assert r.status_code == 400
        assert r.json() == response_400


@pytest.mark.run(order=1)
def test_validate_missing_lpa(server):

    with server.app_context():
        test_data = {
            "code": "hdgeytkvnshd",
            # "lpa": "eed4f597-fd87-4536-99d0-895778824861",
            "dob": "1960-06-05",
        }

        test_headers = {"Content-Type": "application/json"}

        r = requests.post(
            server.url + "/validate", headers=test_headers, data=json.dumps(test_data)
        )

        assert r.status_code == 400
        assert r.json() == response_400


@pytest.mark.run(order=1)
def test_validate_missing_dob(server):

    with server.app_context():
        test_data = {
            "code": "hdgeytkvnshd",
            "lpa": "eed4f597-fd87-4536-99d0-895778824861",
            # "dob": "1960-06-05",
        }

        test_headers = {"Content-Type": "application/json"}

        r = requests.post(
            server.url + "/validate", headers=test_headers, data=json.dumps(test_data)
        )

        assert r.status_code == 400
        assert r.json() == response_400


@pytest.mark.run(order=1)
def test_validate_empty_code(server):

    with server.app_context():
        test_data = {
            "code": "",
            "lpa": "eed4f597-fd87-4536-99d0-895778824861",
            "dob": "1960-06-05",
        }

        test_headers = {"Content-Type": "application/json"}

        r = requests.post(
            server.url + "/validate", headers=test_headers, data=json.dumps(test_data)
        )

        assert r.status_code == 400
        assert r.json() == response_400


@pytest.mark.run(order=1)
def test_validate_empty_lpa(server):

    with server.app_context():
        test_data = {
            "code": "hdgeytkvnshd",
            "lpa": "",
            "dob": "1960-06-05",
        }

        test_headers = {"Content-Type": "application/json"}

        r = requests.post(
            server.url + "/validate", headers=test_headers, data=json.dumps(test_data)
        )

        assert r.status_code == 400
        assert r.json() == response_400


@pytest.mark.run(order=1)
def test_validate_empty_dob(server):

    with server.app_context():
        test_data = {
            "code": "hdgeytkvnshd",
            "lpa": "eed4f597-fd87-4536-99d0-895778824861",
            "dob": "",
        }

        test_headers = {"Content-Type": "application/json"}

        r = requests.post(
            server.url + "/validate", headers=test_headers, data=json.dumps(test_data)
        )

        assert r.status_code == 400
        assert r.json() == response_400
