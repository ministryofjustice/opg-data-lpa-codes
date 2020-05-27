import datetime

import boto3
from boto3.dynamodb.conditions import Key

from lambda_functions.v1.functions.lpa_codes.app.api.database import lpa_codes_table
from lambda_functions.v1.functions.lpa_codes.app.api.endpoints import handle_create

from pytest_cases import CaseDataGetter, cases_data

from lambda_functions.v1.tests.api import cases_handle_create
from lambda_functions.v1.tests.conftest import (
    remove_test_data,
    test_constants,
    insert_test_data,
)


@cases_data(module=cases_handle_create)
def test_post(mock_database, mock_generate_code, case_data: CaseDataGetter):
    test_data, data, expected_result = case_data.get()

    result = handle_create(data=data)

    assert result == expected_result

    remove_test_data(expected_result["codes"])


@cases_data(module=cases_handle_create)
def test_data(mock_database, mock_generate_code, case_data: CaseDataGetter):
    test_data, data, expected_result = case_data.get()

    insert_test_data(test_data=test_data)

    handle_create(data=data)

    lpa = data["lpas"][0]["lpa"]
    actor = data["lpas"][0]["actor"]

    db = boto3.resource("dynamodb")
    table = db.Table(lpa_codes_table())

    query_result = table.query(
        IndexName="key_index",
        KeyConditionExpression=Key("lpa").eq(lpa) & Key("actor").eq(actor),
    )
    print(f"query_result: {query_result}")

    for item in query_result["Items"]:

        if item["code"] == test_constants["DEFAULT_CODE"]:
            assert item["active"] is True
            assert item["status_details"] == "Generated"
            assert item["last_updated_date"] == test_constants["TODAY_ISO"]
            assert item["generated_date"] == test_constants["TODAY_ISO"]
            assert item["expiry_date"] == test_constants["EXPIRY_DATE"]
        else:
            assert item["active"] is False
            assert item["status_details"] == "Superseded"

    remove_test_data(expected_result["codes"] + test_data)
