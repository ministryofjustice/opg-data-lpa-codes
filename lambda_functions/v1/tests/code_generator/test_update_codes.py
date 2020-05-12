import datetime

import boto3

from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    update_codes,
    get_codes,
)
from lambda_functions.v1.tests.code_generator import cases_update_codes
from lambda_functions.v1.tests.code_generator.conftest import (
    insert_test_data,
    remove_test_data,
)


@cases_data(module=cases_update_codes)
def test_update_codes_by_key(mock_database, case_data: CaseDataGetter):
    test_data, key, code, status, expected_result = case_data.get()

    before_test_data = insert_test_data(test_data=test_data)

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

    remove_test_data(test_data)
