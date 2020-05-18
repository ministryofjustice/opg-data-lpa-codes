from pytest_cases import cases_data, CaseDataGetter
from lambda_functions.v1.functions.lpa_codes.app.api.lets_see_about_this import (
    handle_validate,
)
from lambda_functions.v1.tests.api import cases_handle_validate
from lambda_functions.v1.tests.conftest import (
    insert_test_data,
    remove_test_data,
)


@cases_data(module=cases_handle_validate)
def test_post(mock_database, case_data: CaseDataGetter):
    test_data, data, expected_result = case_data.get()
    # Set up test data
    insert_test_data(test_data=test_data)

    result = handle_validate(data=data)

    assert result == expected_result

    remove_test_data(test_data)
