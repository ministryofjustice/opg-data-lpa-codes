import boto3
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import get_codes
from lambda_functions.v1.tests.code_generator import cases_get_codes


@cases_data(module=cases_get_codes)
def test_get_codes(mock_database, case_data: CaseDataGetter):
    test_data, code, key, expected_result, expected_result_count = case_data.get()

    # Set up test data
    table = boto3.resource("dynamodb").Table("lpa_codes")

    for row in test_data:
        table.put_item(Item=row)

    # Run test function
    result = get_codes(code=code, key=key)

    for row in result:

        assert isinstance(row["active"], bool)

    assert len(result) == expected_result_count

    # Tidy up test data
    for row in test_data:
        table.delete_item(Key=row)
