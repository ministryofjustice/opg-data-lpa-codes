import requests


def test_get(server):
    with server.app_context():
        r = requests.get(server.url + "/healthcheck")

        expected_response = "OK"

        assert r.status_code == 200
        assert r.json() == expected_response
