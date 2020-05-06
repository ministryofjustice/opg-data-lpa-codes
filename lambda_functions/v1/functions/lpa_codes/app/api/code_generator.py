import datetime

import boto3
from boto3.dynamodb.conditions import Key


def update_codes_by_key(key, status=False):

    table = boto3.resource("dynamodb").Table("lpa_codes")

    set_active_flag = f"active = {status}"
    set_status_updates = (
        f"last_updated_date = " f"{datetime.datetime.now().strftime('%d/%m/%Y')}"
    )

    all_codes = table.query(
        KeyConditionExpression=Key("lpa").eq(key["lpa"]) & Key("actor").eq(key["actor"])
    )

    print(f"all_codes: {all_codes}")
    for code in all_codes:
        table.update_item(
            Key={"lpa": key["lpa"], "actor": key["actor"]},
            UpdateExpression=f"SET {set_active_flag}, {set_status_updates}",
        )

    return "updated"


def update_codes_by_code(code, status=False):
    table = boto3.resource("dynamodb").Table("lpa_codes")

    set_active_flag = f"active = {status}"
    set_status_updates = (
        f"last_updated_date = " f"{datetime.datetime.now().strftime('%d/%m/%Y')}"
    )

    try:
        key = table.query(
            IndexName="code_index", KeyConditionExpression=Key("code").eq(code)
        )["Items"][0]
    except IndexError:
        return "code does not exist"

    table.update_item(
        Key={"lpa": key["lpa"], "actor": key["actor"], "code": key["code"]},
        UpdateExpression=f"SET {set_active_flag}, {set_status_updates}",
    )

    return "updated"
