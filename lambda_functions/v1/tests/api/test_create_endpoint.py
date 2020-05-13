import requests


def test_post(server):
    with server.app_context():

        data = [
            {
                "lpa": "this is my lpa",
                "actor": "this is my actor",
                "dob": "this is my dob",
            }
        ]

        r = requests.post(server.url + "/create", json=data)

        expected_response = [
            {
                "actor": "this is my actor",
                "code": "this is code",
                "lpa": "this is my lpa",
            }
        ]

        assert r.json() == expected_response
        assert r.status_code == 200
