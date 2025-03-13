import os

import boto3

from .helpers import custom_logger

logger = custom_logger()


def db_connection():
    """
    Sets up the DynamoDB connection. This is different depending on environment. For
    live (aka AWS) it uses boto3 to connect directly to the AWS DynamoDB instance.
    For local/Pact testing it points to a local docker container

    Returns:
        dynamodb resource
    """

    if os.environ.get("ENVIRONMENT") in ["ci", "local"]:
        if os.environ.get("LOCAL_URL"):
            url = os.environ.get("LOCAL_URL")
        else:
            url = "http://localhost:8000"
        conn = boto3.resource(
            "dynamodb", endpoint_url=url, region_name="eu-west-1"
        )
        logger.info(f"Connecting to local Docker database container with url: {url}")
    else:
        conn = boto3.resource("dynamodb")

    return conn


def lpa_codes_table():
    # # TODO these need to be made consistent, no need for this to be a function
    # if os.environ.get("ENVIRONMENT") in ["mock"]:
    #     table_name = "lpa_codes"
    # else:
    table_name = f"lpa-codes-{os.environ.get('ENVIRONMENT')}"
    return table_name
