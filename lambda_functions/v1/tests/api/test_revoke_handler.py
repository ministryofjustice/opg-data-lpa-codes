import boto3
from boto3.dynamodb.conditions import Key

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.functions.lpa_codes.app.api.database import lpa_codes_table
from lambda_functions.v1.functions.lpa_codes.app.api.endpoints import handle_revoke
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.tests.api import cases_handle_revoke
from lambda_functions.v1.tests.conftest import insert_test_data, remove_test_data
from freezegun import freeze_time


@cases_data(module=cases_handle_revoke)
@freeze_time("2020-01-21")
def test_post(mock_database, case_data: CaseDataGetter):
    test_data, data, expected_result, expected_last_updated_date = case_data.get()
    # Set up test data
    insert_test_data(test_data=test_data)

    result = handle_revoke(data=data)

    db = boto3.resource("dynamodb")
    after_revoke = code_generator.get_codes(database=db, code=data["code"])

    assert result == expected_result
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
