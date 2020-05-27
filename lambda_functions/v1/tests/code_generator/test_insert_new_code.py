import datetime
import time
import boto3
from dateutil.relativedelta import relativedelta
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    insert_new_code,
)
from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter
from lambda_functions.v1.tests.code_generator import cases_insert_new_code
from lambda_functions.v1.tests.conftest import test_constants
from freezegun import freeze_time


@cases_data(module=cases_insert_new_code)
@freeze_time("2020-01-21")
def test_insert_new_code(mock_database, case_data: CaseDataGetter):
    key, code, dob, expected_result = case_data.get()
    db = boto3.resource("dynamodb")
    result = insert_new_code(database=db, key=key, dob=dob, code=code)

    table_name = test_constants["TABLE_NAME"]
    table = db.Table(table_name)

    db_row = table.get_item(Key={"code": code})

    print(f"db_row['Item']: {db_row['Item']}")

    today = datetime.datetime.now()
    in_12_months = datetime.datetime.now() + relativedelta(months=+12)

    assert db_row["Item"]["generated_date"] == date_formatter(today)
    assert db_row["Item"]["expiry_date"] == date_formatter(
        date_obj=in_12_months, format="unix"
    )

    assert result == expected_result

    table.delete_item(Key=db_row["Item"])
