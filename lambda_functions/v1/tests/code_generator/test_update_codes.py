import datetime

import boto3
from boto3.dynamodb.conditions import Key
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import update_codes, \
    get_codes
from lambda_functions.v1.tests.code_generator import test_cases_update_codes
from lambda_functions.v1.tests.code_generator.test_cases_update_codes import (
    by_key_test_data,
)


@cases_data(module=test_cases_update_codes)
def test_update_codes_by_key(mock_database, case_data: CaseDataGetter):
    test_data, key, code, status, expected_result = case_data.get()
    table = boto3.resource("dynamodb").Table("lpa_codes")

    # Set up test data
    number_of_rows = len(test_data)
    number_of_active_rows = len([x["active"] for x in test_data if x["active"] is True])
    for row in test_data:
        table.put_item(Item=row)

    # Check test data has been inserted as expected
    before_test_data = get_codes(key=key, code=code)

    assert len(before_test_data) == number_of_rows
    assert len([e['active'] for e in before_test_data if e['active'] is True]) == number_of_active_rows

    # Run test function
    test_result = update_codes(key, status)
    print(f"test_result: {test_result}")

    # Test db contents after function
    after_test_data = get_codes(key=key, code=code)


    for row in after_test_data:
        if row["active"] is True:
            number_of_active_rows += 1

        assert row["active"] == str(status)
        assert row["last_updated_date"] == datetime.datetime.now().strftime("%d/%m/%Y")

    assert test_result == expected_result
    assert len([e['active'] for e in after_test_data if e['active'] is True]) != number_of_active_rows

    # Tidy up test data
    for row in test_data:
        table.delete_item(Key=row)

    after_tidyup_data = get_codes(key=key, code=code)


    assert len(after_tidyup_data) == 0

