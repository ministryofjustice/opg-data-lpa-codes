import datetime

import boto3

from pytest_cases import parametrize_with_cases

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    update_codes,
    get_codes,
)
from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter

from lambda_functions.v1.tests.conftest import (
    insert_test_data,
    remove_test_data,
)


@parametrize_with_cases("test_data, key, code, status, expected_result")
def test_update_codes_by_key(mock_database, test_data, key, code, status, expected_result):

    before_test_data = insert_test_data(test_data=test_data)

    # Set some expectations
    should_get_updated = [r["code"] for r in before_test_data if r["active"] != status]
    status_should_be = status
    last_updated_date_should_be = date_formatter(datetime.datetime.now())

    # Run test function
    db = boto3.resource("dynamodb")
    test_result = update_codes(database=db, key=key, code=code, status=status)

    # Test db contents after function

    after_test_data = get_codes(database=db, key=key, code=code)

    for row in after_test_data:
        assert isinstance(row["active"], bool)
        assert row["active"] == status_should_be
        if row["code"] in should_get_updated:
            assert row["last_updated_date"] == last_updated_date_should_be

    assert test_result == expected_result

    remove_test_data(test_data)
