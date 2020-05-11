import datetime

import boto3

from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    update_codes,
    get_codes,
)
from lambda_functions.v1.tests.code_generator import test_cases_update_codes


@cases_data(module=test_cases_update_codes)
def test_update_codes_by_key(mock_database, case_data: CaseDataGetter):
    test_data, key, code, status, expected_result = case_data.get()

    # TODO this could be a fixture
    # Set up test data
    table = boto3.resource("dynamodb").Table("lpa_codes")
    number_of_rows = len(test_data)
    for row in test_data:
        table.put_item(Item=row)

    # Check test data has been inserted as expected
    before_test_data = get_codes(key=key, code=code)
    assert len(before_test_data) == number_of_rows

    # Set some expectations
    should_get_updated = [r["code"] for r in before_test_data if r["active"] != status]
    status_should_be = status
    last_updated_date_should_be = datetime.datetime.now().strftime("%d/%m/%Y")

    # Run test function
    test_result = update_codes(key=key, code=code, status=status)

    # Test db contents after function

    after_test_data = get_codes(key=key, code=code)

    for row in after_test_data:
        assert isinstance(row["active"], bool)
        assert row["active"] == status_should_be
        if row["code"] in should_get_updated:
            assert row["last_updated_date"] == last_updated_date_should_be

    assert test_result == expected_result

    # TODO this could be a fixture
    # Tidy up test data
    for row in test_data:
        table.delete_item(Key=row)

    after_tidyup_data = get_codes(key=key, code=code)

    assert len(after_tidyup_data) == 0
