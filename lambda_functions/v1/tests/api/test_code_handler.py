import boto3
import pytest
from boto3.dynamodb.conditions import Key
import logging
import datetime
from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.functions.lpa_codes.app.api.database import lpa_codes_table
from lambda_functions.v1.functions.lpa_codes.app.api.endpoints import handle_code

from pytest_cases import CaseDataGetter, cases_data

from lambda_functions.v1.tests.api import cases_handle_code
from lambda_functions.v1.tests.conftest import (
    remove_test_data,
    test_constants,
    insert_test_data,
)


@cases_data(module=cases_handle_code)
def test_post(mock_database, mock_generate_code, case_data: CaseDataGetter):
    test_data, data, expected_result, expected_status_code = case_data.get()

    insert_test_data(test_data)

    result, status_code = handle_code(data=data)

    assert result == expected_result
    assert status_code == expected_status_code

    remove_test_data(test_data)
