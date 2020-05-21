import json

import requests

import pytest


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

        print(f"r: {r}")
        print(f"r.json(): {r.json()}")
        assert r.status_code == 200
        assert r.json() == expected_return
