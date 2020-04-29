import requests


def test_get(server):
    with server.app_context():
        r = requests.get(server.url + "/healthcheck")

        expected_response = {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "well hello there",
        }
        assert r.status_code == 200
        assert r.json() == expected_response
