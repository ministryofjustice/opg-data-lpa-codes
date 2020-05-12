import boto3
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    insert_new_code,
)
from lambda_functions.v1.tests.code_generator import cases_insert_new_code


@cases_data(module=cases_insert_new_code)
def test_insert_new_code(mock_database, case_data: CaseDataGetter):
    key, code, expected_result = case_data.get()

    result = insert_new_code(key=key, code=code)

    print(f"result: {result}")

    assert result == expected_result
