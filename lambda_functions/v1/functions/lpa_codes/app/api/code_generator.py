import datetime
import secrets
from boto3.dynamodb.conditions import Key, Attr

from .database import lpa_codes_table
from .helpers import custom_logger, date_formatter, calculate_expiry_date

logger = custom_logger()


def generate_code(database):
    """
    Generates a 12-digit alphanumeric code containing no ambiguous characters.
    Codes should be unique - we try 10 times and if we can't generate a new code then
    error.

    Args:
        database:

    Returns:
        string
    """
    acceptable_characters = "346789BCDFGHJKMPQRTVWXY"

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
        database:
        code: string

    Returns:
        boolean
    """
    response = get_codes(database=database, code=code)

    if len(response) == 0:
        return True
    return False


def get_codes(database, key=None, code=None):
    """
    Generic method of getting codes from the db either by key (lpa/actor) or code

    Quick check against TTL - AWS claim it can take up to 48 hours to actually remove
    records past their TTL so we are checking manually just to be sure

    Args:
        database:
        key: dict, eg {"lpa":"lpa_id", "actor":"actor_id"}
        code: string

    Returns:
        list: all codes associated with given params

    """

    table = database.Table(lpa_codes_table())

    return_fields = [
        "lpa",
        "actor",
        "code",
        "active",
        "last_updated_date",
        "dob",
        "expiry_date",
        "generated_date",
        "status_details",
    ]

    return_fields = " ,".join(return_fields)

    # TTL cutoff is set to midnight this morning - does not need to be the exact time
    ttl_cutoff = int(
        datetime.datetime.combine(
            datetime.datetime.now(), datetime.datetime.min.time()
        ).timestamp()
    )

    codes = []
    if code:
        query_result = table.get_item(
            Key={"code": code}, ProjectionExpression=return_fields
        )

        try:
            expiry_date = query_result["Item"]["expiry_date"]

            if expiry_date > ttl_cutoff:
                query_result["Item"]["expiry_date"] = int(expiry_date)
                codes.append(query_result["Item"])
            else:
                logger.info("Code does not exist in database")
        except KeyError:
            # TODO better error handling here
            logger.info("Code does not exist in database")

    elif key:
        try:
            lpa = key["lpa"]
            actor = key["actor"]

            query_result = table.query(
                IndexName="key_index",
                KeyConditionExpression=Key("lpa").eq(lpa) & Key("actor").eq(actor),
                FilterExpression=Attr("expiry_date").gt(ttl_cutoff),
                ProjectionExpression=return_fields
            )

            if len(query_result["Items"]) > 0:
                codes.extend(query_result["Items"])
            else:
                # TODO better error handling here
                logger.info("LPA/actor does not exist in database")

        except KeyError:
            # TODO better error handling here
            logger.info("LPA/actor does not exist in database")

    return codes


def update_codes(database, key=None, code=None, status=False, status_details=None, expiry_date=None):
    """
    Generic method to update the status of rows in the db, eithet by key (lpa/actor)
    or code.

    Args:
        database:
        dict, eg {"lpa":"lpa_id", "actor":"actor_id"}
        code: string
        status: boolean
        status_details: string
        expiry_date: string

    Returns:
        int: number of rows updated

    """

    table = database.Table(lpa_codes_table())
    entries = get_codes(database=database, key=key, code=code)

    if len(entries) == 0:
        logger.info(f"0 rows updated for LPA/Actor")
        return 0

    updated_rows = 0
    for entry in entries:
        if entry["active"] != status:
            if expiry_date:
                table.update_item(
                    Key={"code": entry["code"]},
                    UpdateExpression="set active = :a, last_updated_date = :d, "
                    "expiry_date = :e",
                    ExpressionAttributeValues={
                        ":a": status,
                        ":d": date_formatter(datetime.datetime.now()),
                        ":e": expiry_date,
                    },
                )
            else:
                table.update_item(
                    Key={"code": entry["code"]},
                    UpdateExpression="set active = :a, last_updated_date = :d, "
                    "status_details = :s",
                    ExpressionAttributeValues={
                        ":a": status,
                        ":d": date_formatter(datetime.datetime.now()),
                        ":s": status_details,
                    },
                )

            updated_rows += 1
    logger.info(f"{updated_rows} rows updated for LPA/Actor")
    return updated_rows


def insert_new_code(database, key, dob, code):
    """
    Inserts a new code into the db and returns the newly inserted record

    Args:
        database:
        key: dict, eg {"lpa":"lpa_id", "actor":"actor_id"}
        dob: string - should be iso date
        code: string

    Returns:
        list: all codes associated with given params

    """

    table = database.Table(lpa_codes_table())
    lpa = key["lpa"]
    actor = key["actor"]

    item={
            "lpa": lpa,
            "actor": actor,
            "code": code,
            "active": True,
            "last_updated_date": date_formatter(datetime.datetime.now()),
            "dob": dob,
            "generated_date": date_formatter(datetime.datetime.now()),
            "status_details": "Generated",
        }
    if lpa[0] != 'M' : 
        item.update({"expiry_date" : calculate_expiry_date(today=datetime.datetime.now())})
    table.put_item(
        Item=item
    )

    inserted_item = get_codes(database, code=code)

    return inserted_item
