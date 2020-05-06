import datetime

import boto3
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    update_existing_codes,
)
from lambda_functions.v1.tests.code_generator import test_cases_update_existing_codes


@cases_data(module=test_cases_update_existing_codes)
def test_update_existing_codes(mock_database, case_data: CaseDataGetter):
    keys, active_codes, status, expected_result = case_data.get()
    table = boto3.resource("dynamodb").Table("lpa_codes")

    active_code_count = 0
    for key in keys:
        result = table.get_item(
            Key={"lpa": key["lpa"], "actor": key["actor"], "code": key["code"]}
        )
        if result["Item"]["active"] is True:
            active_code_count += 1

    assert active_code_count == active_codes
    update_result = update_existing_codes(keys, status)

    updated_active_code_count = 0
    for key in keys:
        result = table.get_item(
            Key={"lpa": key["lpa"], "actor": key["actor"], "code": key["code"]}
        )
        if result["Item"]["active"] is True:
            active_code_count += 1

        assert result["Item"]["active"] == str(status)
        assert result["Item"]["last_updated_date"] == datetime.datetime.now().strftime(
            "%d/%m/%Y"
        )
        assert updated_active_code_count == 0

    assert update_result == expected_result
