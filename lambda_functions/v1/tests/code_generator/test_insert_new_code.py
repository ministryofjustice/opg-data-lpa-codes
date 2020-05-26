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

from lambda_functions.v1.tests.conftest import remove_test_data, mock_db_table_name


@cases_data(module=cases_insert_new_code)
def test_insert_new_code(mock_database, case_data: CaseDataGetter):
    key, code, dob, expected_result = case_data.get()
    db = boto3.resource("dynamodb")
    result = insert_new_code(database=db, key=key, dob=dob, code=code)

    table_name = mock_db_table_name()
    table = db.Table(table_name)
    return_fields = (
        "lpa, actor, code, active, last_updated_date, dob, "
        "generated_date, expiry_date"
    )
    db_row = table.get_item(Key={"code": code}, ProjectionExpression=return_fields)

    today = datetime.datetime.now()
    in_12_months = datetime.datetime.now() + relativedelta(months=+12)

    assert db_row["Item"]["generated_date"] == date_formatter(today)
    assert db_row["Item"]["expiry_date"] == date_formatter(
        date_obj=in_12_months, format="unix"
    )

    print(f"result: {result}")

    assert result == expected_result

    # remove_test_data(db_row['Item'])
    table.delete_item(Key=db_row["Item"])
