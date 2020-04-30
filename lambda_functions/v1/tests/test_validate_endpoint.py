import requests


def test_post(server):
    with server.app_context():
        r = requests.post(server.url + "/validate", data={})

        expected_response = {
            "code": "example_code",
            "id": "7c94fd39-7680-43a8-ba25-7430760c52b3",
            "status": "valid",
        }

        assert r.status_code == 501
        assert r.json() == expected_response
