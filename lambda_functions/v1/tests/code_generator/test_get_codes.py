import boto3
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.tests.code_generator import cases_get_codes
from lambda_functions.v1.tests.conftest import (
    insert_test_data,
    remove_test_data,
)


@cases_data(module=cases_get_codes)
def test_get_codes(mock_database, case_data: CaseDataGetter):
    test_data, code, key, expected_result, expected_result_count = case_data.get()
    # Set up test data
    insert_test_data(test_data=test_data)

    # Run test function
    db = boto3.resource("dynamodb")
    result = code_generator.get_codes(database=db, code=code, key=key)

    for row in result:

        assert isinstance(row["active"], bool)

    assert len(result) == expected_result_count

    remove_test_data(test_data)
