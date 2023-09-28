import requests

import pytest


@pytest.mark.run(order=1)
def test_healthcheck_get(server):
    with server.app_context():
        r = requests.get(server.url + "/healthcheck")
        assert r.status_code == 200
        assert r.json() == "OK"


@pytest.mark.run(order=1)
def test_healthcheck_head(server):
    with server.app_context():
        r = requests.head(server.url + "/healthcheck")

        assert r.status_code == 200
