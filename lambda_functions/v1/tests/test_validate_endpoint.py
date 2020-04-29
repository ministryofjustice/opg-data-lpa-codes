import requests


def test_post(server):
    with server.app_context():
        r = requests.post(server.url + "/validate", data={})

        expected_response = {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "valid",
        }

        assert r.status_code == 200
        assert r.json() == expected_response
