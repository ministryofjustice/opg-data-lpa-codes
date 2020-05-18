import boto3

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.functions.lpa_codes.app.api.lets_see_about_this import (
    handle_revoke,
)
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.tests.api import cases_handle_revoke
from lambda_functions.v1.tests.conftest import (
    insert_test_data,
    remove_test_data,
)


@cases_data(module=cases_handle_revoke)
def test_post(mock_database, case_data: CaseDataGetter):
    test_data, data, expected_result, expected_last_updated_date = case_data.get()
    # Set up test data
    insert_test_data(test_data=test_data)

    result = handle_revoke(data=data)

    db = boto3.resource("dynamodb")
    after_revoke = code_generator.get_codes(database=db, code=data["code"])

    assert result == expected_result
    if after_revoke:
        assert after_revoke[0]["last_updated_date"] == expected_last_updated_date

    remove_test_data(test_data)
