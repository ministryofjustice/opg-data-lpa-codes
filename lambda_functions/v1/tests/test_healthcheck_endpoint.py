import requests


def test_get(server):
    with server.app_context():
        r = requests.get(server.url + "/healthcheck")

        assert r.status_code == 200
        assert r.text == "ok"
