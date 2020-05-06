import requests


def test_post(server):
    with server.app_context():
        r = requests.post(server.url + "/create", data={})

        expected_response = {
            "code": "example_code",
            "id": "91d9860e-f759-4214-8ffa-bfd87a12a995",
            "status": "generated",
        }
        assert r.status_code == 501
        assert r.json() == expected_response
