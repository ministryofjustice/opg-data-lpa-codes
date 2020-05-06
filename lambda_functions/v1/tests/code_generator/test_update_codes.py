import datetime

import boto3
from boto3.dynamodb.conditions import Key
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import (
    update_codes_by_key,
    update_codes_by_code,
)
from lambda_functions.v1.tests.code_generator import test_cases_update_codes
from lambda_functions.v1.tests.code_generator.test_cases_update_codes import (
    by_key_test_data,
)


@cases_data(module=test_cases_update_codes, has_tag="by key")
def test_update_codes_by_key(mock_database, case_data: CaseDataGetter):
    key, active_codes, status, expected_result = case_data.get()
    table = boto3.resource("dynamodb").Table("lpa_codes")

    data = by_key_test_data()
    number_of_codes = len(data)
    active_code_count = len([x["active"] for x in data if x["active"] is True])
    assert active_code_count == active_codes

    for row in data:
        table.put_item(Item=row)

    filter = Key("lpa").eq(key["lpa"]) and Key("actor").eq(key["actor"])
    before_update_data = table.scan(FilterExpression=filter)

    print(f"before_update_data: {before_update_data['Items']}")
    assert len(before_update_data["Items"]) == number_of_codes

    update_result = update_codes_by_key(key, status)

    result = table.query(
        KeyConditionExpression=Key("lpa").eq(key["lpa"]) & Key("actor").eq(key["actor"])
    )

    print(f"result: {len(result)}")
    for row in result["Items"]:
        if row["active"] is True:
            active_code_count += 1

        assert row["active"] == str(status)
        assert row["last_updated_date"] == datetime.datetime.now().strftime("%d/%m/%Y")

    assert update_result == expected_result
    assert 1 == 5

    for row in data:
        table.delete_item(Key=row)


@cases_data(module=test_cases_update_codes, has_tag="by code")
def test_update_codes_by_code(mock_database, case_data: CaseDataGetter):
    code, status, expected_result = case_data.get()
    table = boto3.resource("dynamodb").Table("lpa_codes")

    data = by_key_test_data()
    for row in data:
        table.put_item(Item=row)

    update_result = update_codes_by_code(code, status)

    assert update_result == expected_result

    if update_result == "updated":

        result = table.query(
            IndexName="code_index", KeyConditionExpression=Key("code").eq(code)
        )

        assert result["Items"][0]["active"] == str(status)
        assert result["Items"][0][
            "last_updated_date"
        ] == datetime.datetime.now().strftime("%d/%m/%Y")

    for row in data:
        table.delete_item(Key=row)
