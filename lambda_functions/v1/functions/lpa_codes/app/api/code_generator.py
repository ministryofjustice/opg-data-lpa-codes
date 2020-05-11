import datetime
import secrets

import boto3
from boto3.dynamodb.conditions import Key, Attr
import os

from flask import logging

from lambda_functions.v1.functions.lpa_codes.app.api.helpers import custom_logger

logger = custom_logger("code generator")


def generate_code():
    acceptable_characters = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"

    unique = False
    attempts = 0
    max_attempts = 10

    while unique is not True:
        new_code = "".join(secrets.choice(acceptable_characters) for i in range(0, 12))
        unique = check_code_unique(new_code)
        attempts += 1
        if attempts == max_attempts:
            logger.error("Unable to generate unique code - failed after 10 attempts")
            new_code = None
            break
    return new_code


def check_code_unique(code):
    return True




def check_code_unique(code):
    return True


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
            # TODO better error handling here
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
            # TODO better error handling here
            print("key does not exist")

    return codes


def update_codes(key=None, code=None, status=False):

    table = boto3.resource("dynamodb").Table("lpa_codes")

    entries = get_codes(key=key, code=code)

    updated_rows = 0
    for entry in entries:
        if entry["active"] != status:

            table.update_item(
                Key={"code": entry["code"]},
                UpdateExpression="set active = :a, last_updated_date = :d",
                ExpressionAttributeValues={
                    ":a": status,
                    ":d": datetime.datetime.now().strftime("%d/%m/%Y"),
                },
            )

            updated_rows += 1

    return updated_rows
