import requests


def test_post(server):
    with server.app_context():
        r = requests.post(server.url + "/create", data={})

        assert r.status_code == 200
        assert r.json() == {"message": "code created"}
