import logging

import boto3
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    check_code_unique,
)
from lambda_functions.v1.tests.code_generator import cases_check_code_unique
from lambda_functions.v1.tests.code_generator.conftest import (
    insert_test_data,
    remove_test_data,
)


@cases_data(module=cases_check_code_unique)
def test_check_code_unique(mock_database, caplog, case_data: CaseDataGetter):
    test_data, code, logger_message, expected_result = case_data.get()

    insert_test_data(test_data=test_data)

    result = check_code_unique(code)

    assert result == expected_result
    with caplog.at_level(logging.INFO):
        assert logger_message in caplog.text

    remove_test_data(test_data)
