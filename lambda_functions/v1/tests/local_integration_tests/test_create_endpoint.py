import pytest
import requests


@pytest.mark.skip(reason="requires local dynamodb setup")
def test_post(server, mock_generate_code):
    with server.app_context():

        data = [
            {
                "lpa": "this is my lpa",
                "actor": "this is my actor",
                "dob": "this is my dob",
            }
        ]

        r = requests.post(server.url + "/create", json=data)

        expected_response = [
            {
                "actor": "this is my actor",
                "code": "idFCGZIvjess",
                "lpa": "this is my lpa",
            }
        ]

        assert r.json() == expected_response
        assert r.status_code == 200
