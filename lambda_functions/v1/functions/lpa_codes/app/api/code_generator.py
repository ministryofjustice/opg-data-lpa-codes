import datetime

import boto3
from boto3.dynamodb.conditions import Key, Attr


def get_codes(key=None, code=None):
    table = boto3.resource("dynamodb").Table("lpa_codes")
    return_fields = "lpa, actor, code"

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
