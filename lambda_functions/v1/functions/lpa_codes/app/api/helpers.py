import logging
import os

import boto3


def custom_logger(name):
    formatter = logging.Formatter(
        fmt=f"%(asctime)s - %(levelname)s - {name} - in %("
        f"funcName)s:%(lineno)d - %(message)s"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    try:
        logger.setLevel(os.environ["LOGGER_LEVEL"])
    except KeyError:
        logger.setLevel("INFO")
    logger.addHandler(handler)
    return logger


def db_client():
    return boto3.resource("dynamodb", endpoint_url="http://localhost:8000")


def db_tables():
    logger = custom_logger("helpers")

    logger.info("real table name generator")
    return f"lpa-codes-{os.environ['ENVIRONMENT']}"
