import json

import requests

import pytest


@pytest.mark.run(order=1)
def test_revoke(server):

    with server.app_context():
        test_data = {"code": "hdgeytkvnshd"}

        test_headers = {"Content-Type": "application/json"}

        expected_return = {"codes revoked": 0}

        r = requests.post(
            server.url + "/revoke", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 200
        assert r.json() == expected_return
