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
def test_create(server):

    with server.app_context():
        test_data = {
            "lpas": [
                {
                    "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                    "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                    "dob": "1960-06-05",
                }
            ]
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = {
            "codes": [
                {
                    "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                    "code": "tOhkrldOqewm",
                    "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                }
            ]
        }

        r = requests.post(
            server.url + "/create", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 200
        assert r.json() == expected_return


@pytest.mark.run(order=1)
def test_create_missing_lpa(server):

    with server.app_context():
        test_data = {
            "lpas": [
                {
                    # "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                    "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                    "dob": "1960-06-05",
                }
            ]
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400

        r = requests.post(
            server.url + "/create", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return


@pytest.mark.run(order=1)
def test_create_missing_actor(server):

    with server.app_context():
        test_data = {
            "lpas": [
                {
                    "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                    # "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                    "dob": "1960-06-05",
                }
            ]
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400

        r = requests.post(
            server.url + "/create", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return


@pytest.mark.run(order=1)
def test_create_missing_dob(server):

    with server.app_context():
        test_data = {
            "lpas": [
                {
                    "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                    "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                    # "dob": "1960-06-05",
                }
            ]
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400

        r = requests.post(
            server.url + "/create", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return


@pytest.mark.run(order=1)
def test_create_empty_lpa(server):

    with server.app_context():
        test_data = {
            "lpas": [
                {
                    "lpa": "",
                    "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                    "dob": "1960-06-05",
                }
            ]
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400

        r = requests.post(
            server.url + "/create", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return


@pytest.mark.run(order=1)
def test_create_empty_actor(server):

    with server.app_context():
        test_data = {
            "lpas": [
                {
                    "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                    "actor": "",
                    "dob": "1960-06-05",
                }
            ]
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400

        r = requests.post(
            server.url + "/create", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return


@pytest.mark.run(order=1)
def test_create_empty_dob(server):

    with server.app_context():
        test_data = {
            "lpas": [
                {
                    "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                    "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                    "dob": "",
                }
            ]
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400

        r = requests.post(
            server.url + "/create", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return
