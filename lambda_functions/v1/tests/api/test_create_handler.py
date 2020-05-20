from lambda_functions.v1.functions.lpa_codes.app.api.endpoints import handle_create

from pytest_cases import CaseDataGetter, cases_data

from lambda_functions.v1.tests.api import cases_handle_create
from lambda_functions.v1.tests.conftest import remove_test_data


@cases_data(module=cases_handle_create)
def test_post(mock_database, mock_generate_code, case_data: CaseDataGetter):
    data, expected_result = case_data.get()

    result = handle_create(data=data)

    assert result == expected_result

    remove_test_data(expected_result["codes"])
