import logging
import os

import boto3


def custom_logger(name=None):
    logger_name = name if name else "lpa_code_generator"
    formatter = logging.Formatter(
        fmt=f"%(asctime)s - %(levelname)s - {logger_name} - in %("
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


# def db():
#     if os.environ.get("ENVIRONMENT") in ["ci", "local"]:
#         db = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")
#     else:
#         db = boto3.resource("dynamodb")
#
#     return db


# def db_table_name(table_name_base=None):
#     default_table_name = "lpa_codes"
#
#     suffix = os.environ.get("ENVIRONMENT") if os.environ.get("ENVIRONMENT") else ""
#     base = table_name_base if table_name_base else default_table_name
#     return f"{base}_{suffix}"
