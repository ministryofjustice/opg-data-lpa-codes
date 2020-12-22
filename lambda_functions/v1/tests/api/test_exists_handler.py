import logging

from pytest_cases import cases_data, CaseDataGetter
from lambda_functions.v1.functions.lpa_codes.app.api.endpoints import handle_exists
from lambda_functions.v1.tests.api import cases_handle_exists
from lambda_functions.v1.tests.conftest import (
    insert_test_data,
    remove_test_data,
)


@cases_data(module=cases_handle_exists)
def test_post(mock_database, case_data: CaseDataGetter):
    test_data, data, expected_result, expected_status_code = case_data.get()
    # Set up test data
    insert_test_data(test_data=test_data)

    result, status_code = handle_exists(data=data)

    assert result == expected_result
    assert status_code == expected_status_code

    remove_test_data(test_data)


