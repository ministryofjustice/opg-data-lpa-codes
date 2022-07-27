import json


import requests
import pytest


response_400 = {
    "body": {"error": {"code": "Bad Request", "message": "Bad payload"}},
    "headers": {"Content-Type": "application/json"},
    "isBase64Encoded": False,
    "statusCode": 400,
}


@pytest.mark.run(order=1)
def test_code(server):

    with server.app_context():
        test_data = {
           "code": "hdgeytkvnshd"
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = [
                {
                    'active': True, 
                    'actor': '12ad81a9-f89d-4804-99f5-7c0c8669ac9b', 
                    'code': 'hdgeytkvnshd',
                    'dob': None,
                    'generated_date': '2019-11-10',
                    'last_updated_date': '2022-07-27',
                    'lpa': 'eed4f597-fd87-4536-99d0-895778824861'
                }
            ]
        

        r = requests.post(
            server.url + "/code", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 200
        assert r.json() == expected_return

@pytest.mark.run(order=1)
def test_missing_input(server):

    with server.app_context():
        test_data = {
        #    "code": "hdgeytkvnshd"
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400
        

        r = requests.post(
            server.url + "/code", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return
        
@pytest.mark.run(order=1)
def test_empty_input(server):

    with server.app_context():
        test_data = {
            "code": ""
        }

        test_headers = {"Content-Type": "application/json"}

        expected_return = response_400
        

        r = requests.post(
            server.url + "/code", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 400
        assert r.json() == expected_return
        
        
@pytest.mark.run(order=1)
def test_code_not_found(server):
    
    response_404 = {
    "body": {"error": {"code": "Not Found", "message": "Not found url " + server.url + "/code"}},
    "headers": {"Content-Type": "application/json"},
    "isBase64Encoded": False,
    "statusCode": 404,
}

    with server.app_context():
        test_data = {
            "code": "NonExistentCode"
        }

        test_headers = {"Content-Type": "application/json"}   
        
        expected_return = response_404     

        r = requests.post(
            server.url + "/code", headers=test_headers, data=json.dumps(test_data)
        )
        assert r.status_code == 404
        assert r.json() == expected_return
