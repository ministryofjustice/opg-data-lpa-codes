import logging
from lambda_functions.v1.functions.lpa_codes.app.api.endpoints import handle_code

from pytest_cases import parametrize_with_cases

from lambda_functions.v1.tests.conftest import (
    remove_test_data,
    test_constants,
    insert_test_data,
)


@parametrize_with_cases("test_data, data, expected_result, expected_status_code")
def test_post(mock_database, mock_generate_code, test_data, data, expected_result, expected_status_code):

    insert_test_data(test_data)

    result, status_code = handle_code(data=data)

    assert result == expected_result
    assert status_code == expected_status_code

    remove_test_data(test_data)


@parametrize_with_cases("test_data, data, expected_result, expected_status_code")
def test_get_codes_broken(
    mock_database,
    mock_generate_code,
    broken_get_code,
    caplog,
    test_data,
    data, 
    expected_result, 
    expected_status_code 
):

    result, status_code = handle_code(data=data)

    assert status_code == 500
    with caplog.at_level(logging.ERROR):
        assert "get_codes" in caplog.text
