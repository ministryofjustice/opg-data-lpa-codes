import os

import boto3

from .helpers import custom_logger

logger = custom_logger()


def db_connection():

    if os.environ.get("ENVIRONMENT") in ["ci", "local"]:
        if os.environ.get("LOCAL_URL"):
            url = "host.docker.internal"
        else:
            url = "localhost"
        conn = boto3.resource(
            "dynamodb", endpoint_url="http://" + url + ":8000", region_name="eu-west-1"
        )
        logger.info(f"Connecting to local Docker database container with url: {url}")
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
