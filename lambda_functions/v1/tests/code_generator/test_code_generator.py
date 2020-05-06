import datetime

import boto3
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    update_existing_codes,
)
from lambda_functions.v1.tests.code_generator import test_cases_update_existing_codes


@cases_data(module=test_cases_update_existing_codes)
def test_update_existing_codes(mock_database, case_data: CaseDataGetter):
    keys, status, expected_result = case_data.get()

    update_result = update_existing_codes(keys, status)

    table = boto3.resource("dynamodb").Table("lpa_codes")

    for key in keys:
        result = table.get_item(
            Key={"lpa": key["lpa"], "actor": key["actor"], "code": key["code"]}
        )
        assert result["Item"]["active"] == str(status)
        assert result["Item"]["last_updated_date"] == datetime.datetime.now().strftime(
            "%d/%m/%Y"
        )

        print(result["Item"])
    assert 1 == 5
    assert update_result == expected_result
