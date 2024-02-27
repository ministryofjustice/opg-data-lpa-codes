import logging

import boto3
from pytest_cases import parametrize_with_cases

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    check_code_unique,
)
from lambda_functions.v1.tests.conftest import (
    insert_test_data,
    remove_test_data,
)

@parametrize_with_cases("test_data, code, logger_message, expected_result")
def test_check_code_unique(mock_database, caplog, test_data, code, logger_message, expected_result):

    insert_test_data(test_data=test_data)
    db = boto3.resource("dynamodb")
    result = check_code_unique(database=db, code=code)

    assert result == expected_result
    with caplog.at_level(logging.INFO):
        assert logger_message in caplog.text

    remove_test_data(test_data)
