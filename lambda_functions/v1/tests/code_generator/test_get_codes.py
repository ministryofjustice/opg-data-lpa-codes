import boto3
import pytest
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes import app
from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.tests.code_generator import cases_get_codes


@cases_data(module=cases_get_codes)
def test_get_codes(mock_db_tables, mock_database, case_data: CaseDataGetter):
    test_data, code, key, expected_result, expected_result_count = case_data.get()
    # Set up test data
    db = boto3.resource("dynamodb")
    table = db.Table("lpa_codes")

    for row in test_data:
        table.put_item(Item=row)

    # Run test function
    result = code_generator.get_codes(database=db, code=code, key=key)

    for row in result:

        assert isinstance(row["active"], bool)

    assert len(result) == expected_result_count

    # Tidy up test data
    for row in test_data:
        table.delete_item(Key=row)
