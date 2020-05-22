import datetime
import secrets
from boto3.dynamodb.conditions import Key

from .database import lpa_codes_table
from .helpers import custom_logger, date_formatter

logger = custom_logger()


def generate_code(database):
    """
    Generates a 12-digit alphanumeric code containing no ambiguous characters.
    Codes should be unique.
    Codes should not be reused.

    Returns:
        string
    """
    acceptable_characters = "3456789abcdefghijkmnpqrstuvwxyABCDEFGHJKLMNPQRSTUVWXY"

    unique = False
    attempts = 0
    max_attempts = 10

    while unique is not True:
        new_code = "".join(secrets.choice(acceptable_characters) for i in range(0, 12))
        unique = check_code_unique(database=database, code=new_code)
        attempts += 1
        if attempts == max_attempts:
            logger.error("Unable to generate unique code - failed after 10 attempts")
            new_code = None
            break
    return new_code


def check_code_unique(database, code):
    """
    Check the new code we've generated has not been used before
    Args:
        code: string

    Returns:
        boolean
    """
    response = get_codes(database=database, code=code)

    print(f"response: {response}")

    if len(response) == 0:
        return True
    return False


def get_codes(database, key=None, code=None):

    table = database.Table(lpa_codes_table())

    return_fields = "lpa, actor, code, active, last_updated_date, dob"

    codes = []
    if code:
        query_result = table.get_item(
            Key={"code": code}, ProjectionExpression=return_fields
        )

        try:
            codes.append(query_result["Item"])
        except KeyError:
            # TODO better error handling here
            logger.info("Code does not exist in database")

    elif key:
        lpa = key["lpa"]
        actor = key["actor"]
        query_result = table.query(
            IndexName="key_index",
            KeyConditionExpression=Key("lpa").eq(lpa) & Key("actor").eq(actor),
            ProjectionExpression=return_fields,
        )

        if len(query_result["Items"]) > 0:
            codes.extend(query_result["Items"])
        else:
            # TODO better error handling here
            logger.info("LPA/actor does not exist in database")

    return codes


def update_codes(database, key=None, code=None, status=False):

    table = database.Table(lpa_codes_table())
    entries = get_codes(database=database, key=key, code=code)
    logger.info(f"entries: {entries}")
    if len(entries) == 0:
        logger.info(f"0 rows updated for LPA/Actor")
        return 0

    updated_rows = 0
    for entry in entries:
        if entry["active"] != status:

            table.update_item(
                Key={"code": entry["code"]},
                UpdateExpression="set active = :a, last_updated_date = :d",
                ExpressionAttributeValues={
                    ":a": status,
                    ":d": date_formatter(datetime.datetime.now()),
                },
            )

            updated_rows += 1
    logger.info(f"{updated_rows} rows updated for LPA/Actor")
    return updated_rows


def insert_new_code(database, key, dob, code):

    table = database.Table(lpa_codes_table())
    lpa = key["lpa"]
    actor = key["actor"]

    table.put_item(
        Item={
            "lpa": lpa,
            "actor": actor,
            "code": code,
            "active": True,
            "last_updated_date": date_formatter(datetime.datetime.now()),
            "dob": dob,
        }
    )

    inserted_item = get_codes(database, code=code)

    return inserted_item
