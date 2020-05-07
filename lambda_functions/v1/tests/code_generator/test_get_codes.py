import boto3
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import get_codes
from lambda_functions.v1.tests.code_generator import test_cases_get_codes


@cases_data(module=test_cases_get_codes)
def test_get_codes(mock_database, case_data: CaseDataGetter):
    code, key, expected_result, expected_result_count = case_data.get()

    result = get_codes(code=code, key=key)

    for row in result:
        assert isinstance(row["active"], bool)

    assert len(result) == expected_result_count
