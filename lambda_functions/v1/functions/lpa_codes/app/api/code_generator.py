import datetime

import boto3
from boto3.dynamodb.conditions import Key, Attr
import os


def get_codes(key=None, code=None):

    table = boto3.resource("dynamodb").Table("lpa_codes")
    return_fields = "lpa, actor, code, active, last_updated_date"

    codes = []

    if code:
        query_result = table.get_item(
            Key={"code": code}, ProjectionExpression=return_fields
        )

        try:
            codes.append(query_result["Item"])
        except KeyError:
            print("code does not exist")

    elif key:
        lpa = key["lpa"]
        actor = key["actor"]
        query_result = table.query(
            IndexName="key_index",
            KeyConditionExpression=Key("lpa").eq(lpa),
            FilterExpression=Attr("actor").eq(actor),
            ProjectionExpression=return_fields,
        )

        if len(query_result["Items"]) > 0:
            codes.extend(query_result["Items"])
        else:
            print("key does not exist")

    return codes


def update_codes(key=None, code=None, status=False):

    table = boto3.resource("dynamodb").Table("lpa_codes")

    set_active_flag = f"active = {status}"
    set_status_updates = (
        f"last_updated_date = " f"{datetime.datetime.now().strftime('%d/%m/%Y')}"
    )

    entries = get_codes(key=key, code=code)

    print(f"entries: {entries}")
    for entry in entries:
        print(f"entry: {entry}")
        table.update_item(
            Key={"code": entry["code"]},
            UpdateExpression=f"SET {set_active_flag}, {set_status_updates}",
        )

    return "updated"
