import json

import requests

import pytest


@pytest.mark.run(order=1)
def test_404(server):
    r = requests.get(server.url + "/not-found")
    assert r.status_code == 404
    data = r.json()
    assert "error" in data["body"]
    assert "Not found" in data["body"]["error"]["message"]


@pytest.mark.run(order=1)
def test_405(server):
    r = requests.get(server.url + "/create")
    assert r.status_code == 405
    data = r.json()
    assert "error" in data["body"]
    assert "Method not supported" in data["body"]["error"]["message"]


@pytest.mark.run(order=1)
def test_500(server, mock_broken_method):
    with server.app_context():
        test_data = {
            "code": "hdgeytkvnshd",
            "lpa": "eed4f597-fd87-4536-99d0-895778824861",
            "dob": "1960-06-05",
        }

        test_headers = {"Content-Type": "application/json"}

        r = requests.post(
            server.url + "/validate", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 500
        data = r.json()
        assert "error" in data["body"]
        assert "Something went wrong" in data["body"]["error"]["message"]
