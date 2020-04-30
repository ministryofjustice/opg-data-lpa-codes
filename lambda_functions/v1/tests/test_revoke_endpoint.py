import requests


def test_post(server):
    with server.app_context():
        r = requests.post(server.url + "/revoke", data={})

        expected_response = {
            "code": "example_code",
            "id": "33857363-76cb-4d7e-9f1f-740e04a5456d",
            "status": "revoked",
        }

        assert r.status_code == 501
        assert r.json() == expected_response
