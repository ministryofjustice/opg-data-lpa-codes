import json


import requests
import pytest


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
