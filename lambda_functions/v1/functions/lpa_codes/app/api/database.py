import os

import boto3

from .helpers import custom_logger

logger = custom_logger()


def db_connection():
    if os.environ.get("ENVIRONMENT") in ["ci", "local"]:
        conn = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")
        logger.info("Connecting to local Docker database container")
    else:
        conn = boto3.resource("dynamodb")

    return conn


def lpa_codes_table():
    # TODO these need to be made consistent, no need for this to be a function
    if os.environ.get("ENVIRONMENT") in ["mock"]:
        table_name = "lpa_codes"
    else:
        table_name = f"lpa-codes-{os.environ.get('ENVIRONMENT')}"
    return table_name
