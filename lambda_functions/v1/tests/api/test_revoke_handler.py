import logging
import datetime
import boto3
from boto3.dynamodb.conditions import Key

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.functions.lpa_codes.app.api.database import lpa_codes_table
from lambda_functions.v1.functions.lpa_codes.app.api.endpoints import handle_revoke
from pytest_cases import parametrize_with_cases

from lambda_functions.v1.tests.conftest import insert_test_data, remove_test_data
from freezegun import freeze_time


@parametrize_with_cases("test_data, data, expected_result, expected_last_updated_date, expected_status_code")
@freeze_time(datetime.date.today())
def test_post(mock_database, 
    test_data,
    data,
    expected_result,
    expected_last_updated_date,
    expected_status_code,
):
    # Set up test data
    insert_test_data(test_data=test_data)

    # Perform revoke & check return
    result, status_code = handle_revoke(data=data)
    assert result == expected_result
    assert status_code == expected_status_code

    # Check the data after revoke has been performed
    db = boto3.resource("dynamodb")
    after_revoke = code_generator.get_codes(database=db, code=data["code"])

    if after_revoke:
        lpa = after_revoke[0]["lpa"]
        actor = after_revoke[0]["actor"]

        db = boto3.resource("dynamodb")
        table = db.Table(lpa_codes_table())

        query_result = table.query(
            IndexName="key_index",
            KeyConditionExpression=Key("lpa").eq(lpa) & Key("actor").eq(actor),
        )

        row_data = query_result["Items"][0]

        if data["code"] == row_data["code"]:
            assert row_data["last_updated_date"] == expected_last_updated_date
            assert row_data["status_details"] in [
                "Revoked",
                "Superseded",
            ]
            assert row_data["active"] is False

    remove_test_data(test_data)


@parametrize_with_cases("test_data, data, expected_result, expected_last_updated_date,expected_status_code")
def test_get_codes_broken(
    mock_database,
    mock_generate_code,
    broken_update_codes,
    caplog,
    test_data,
    data,
    expected_result,
    expected_last_updated_date,
    expected_status_code,
):

    result, status_code = handle_revoke(data=data)

    assert status_code == 500
    with caplog.at_level(logging.ERROR):
        assert "update_codes" in caplog.text
