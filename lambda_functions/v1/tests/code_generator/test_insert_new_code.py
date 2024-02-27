import datetime
import time
import boto3
from dateutil.relativedelta import relativedelta
from pytest_cases import parametrize_with_cases

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    insert_new_code,
)
from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter
from lambda_functions.v1.tests.code_generator import cases_insert_new_code
from lambda_functions.v1.tests.conftest import test_constants
from freezegun import freeze_time


@parametrize_with_cases(key, code, dob, expected_result, expected_status_row)
@freeze_time(datetime.date.today())
def test_insert_new_code(mock_database, key, code, dob, expected_result, expected_row):
    db = boto3.resource("dynamodb")
    result = insert_new_code(database=db, key=key, dob=dob, code=code)

    table_name = test_constants["TABLE_NAME"]
    table = db.Table(table_name)

    db_row = table.get_item(Key={"code": code})

    assert result == expected_result
    assert db_row["Item"] == expected_row

    table.delete_item(Key=db_row["Item"])
