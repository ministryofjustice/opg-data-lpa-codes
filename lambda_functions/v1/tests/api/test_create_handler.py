import boto3
import pytest
from boto3.dynamodb.conditions import Key
import logging
import datetime
from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.functions.lpa_codes.app.api.database import lpa_codes_table
from lambda_functions.v1.functions.lpa_codes.app.api.endpoints import handle_create

from pytest_cases import parametrize_with_cases

from lambda_functions.v1.tests.api import cases_handle_create
from lambda_functions.v1.tests.conftest import (
    remove_test_data,
    test_constants,
    insert_test_data,
)
from freezegun import freeze_time


@parametrize_with_cases(test_data, data, expected_result, expected_status_code)
def test_post(mock_database, mock_generate_code, test_data, data, expected_result, expected_status_code):

    result, status_code = handle_create(data=data)

    assert result == expected_result
    assert status_code == expected_status_code

    if expected_result["codes"] is not None:
        remove_test_data(expected_result["codes"])


@parametrize_with_cases(test_data, data, expected_result, expected_status_code)
@freeze_time(datetime.date.today())
def test_data(mock_database, mock_generate_code, test_data, data, expected_result, expected_status_code):

    insert_test_data(test_data=test_data)

    codes_created, status_code = handle_create(data=data)

    for i, item in enumerate(data):

        try:
            lpa = data["lpas"][i]["lpa"]

            actor = data["lpas"][i]["actor"]

            dob = data["lpas"][i]["dob"]
        except KeyError:
            assert codes_created == expected_result
            assert status_code == expected_status_code
            break

        if "" not in [lpa, actor, dob]:

            db = boto3.resource("dynamodb")
            table = db.Table(lpa_codes_table())

            query_result = table.query(
                IndexName="key_index",
                KeyConditionExpression=Key("lpa").eq(lpa) & Key("actor").eq(actor),
            )

            print(f"query_result: {query_result}")

            for item in query_result["Items"]:

                if item["code"] == test_constants["DEFAULT_CODE"]:
                    assert item["dob"] == dob
                    assert item["active"] is True
                    assert item["status_details"] == "Generated"
                    assert item["last_updated_date"] == test_constants["TODAY_ISO"]
                    assert item["generated_date"] == test_constants["TODAY_ISO"]
                    assert item["expiry_date"] == test_constants["EXPIRY_DATE"]
                else:
                    assert item["active"] is False
                    assert item["status_details"] == "Superseded"
        else:
            assert codes_created == expected_result
            break

    if expected_result["codes"] is not None:
        remove_test_data(expected_result["codes"] + test_data)
    else:
        remove_test_data(test_data)


@parametrize_with_cases(test_data, data, expected_result, expected_status_code)
def test_get_codes_broken(
    mock_database,
    mock_generate_code,
    broken_get_code,
    caplog,
    test_data, 
    data, 
    expected_result, 
    expected_status_code 
):

    result, status_code = handle_create(data=data)

    assert status_code == 500
    with caplog.at_level(logging.ERROR):
        assert "get_codes" in caplog.text


@parametrize_with_cases(test_data, data, expected_result, expected_status_code)
def test_generate_code_broken(
    mock_database,
    mock_generate_code,
    broken_generate_code,
    caplog,
    test_data, 
    data, 
    expected_result, 
    expected_status_code 
):

    result, status_code = handle_create(data=data)

    assert status_code == 500
    with caplog.at_level(logging.ERROR):
        assert "generate_code" in caplog.text


@parametrize_with_cases(test_data, data, expected_result, expected_status_code)
def test_insert_new_code_broken(
    mock_database,
    mock_generate_code,
    broken_insert_new_code,
    caplog,
    test_data, 
    data, 
    expected_result, 
    expected_status_code 
):

    result, status_code = handle_create(data=data)

    assert status_code == 500

    with caplog.at_level(logging.ERROR):
        assert "insert_new_code" in caplog.text
