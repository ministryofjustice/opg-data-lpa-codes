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
def test_revoke(server):

    with server.app_context():
        test_data = {"code": "hdgeytkvnshd"}

        test_headers = {"Content-Type": "application/json"}

        expected_return = {"codes revoked": 0}

        r = requests.post(
            server.url + "/revoke", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 200
        assert r.json() == expected_return


@pytest.mark.run(order=1)
def test_revoke_empty_code(server):

    with server.app_context():
        test_data = {"code": ""}

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400

        r = requests.post(
            server.url + "/revoke", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return


@pytest.mark.run(order=1)
def test_revoke_missing_code(server):

    with server.app_context():
        test_data = {"banana": "chipmunk"}

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400

        r = requests.post(
            server.url + "/revoke", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return
