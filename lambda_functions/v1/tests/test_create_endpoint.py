import requests


def test_post(server):
    with server.app_context():
        r = requests.post(server.url + "/create", data={})

        expected_response = {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "created",
        }
        assert r.status_code == 200
        assert r.json() == expected_response
