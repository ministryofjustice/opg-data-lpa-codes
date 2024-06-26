import boto3
from pytest_cases import parametrize_with_cases

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.tests.conftest import (
    insert_test_data,
    remove_test_data,
)
import logging


@parametrize_with_cases("test_data, code, key, expected_result, expected_result_count, expected_logger_message")
def test_get_codes(mock_database, caplog, 
    test_data,
    code,
    key,
    expected_result,
    expected_result_count,
    expected_logger_message,
):
    # Set up test data
    insert_test_data(test_data=test_data)

    # Run test function
    db = boto3.resource("dynamodb")
    result = code_generator.get_codes(database=db, code=code, key=key)

    assert len(result) == expected_result_count

    if expected_result_count == 0:
        with caplog.at_level(logging.INFO):
            assert expected_logger_message in caplog.text

    for row in result:

        assert isinstance(row["active"], bool)
        if code:
            assert code == row["code"]
        if key:
            assert key["lpa"] == row["lpa"]
            assert key["actor"] == row["actor"]

    remove_test_data(test_data)
