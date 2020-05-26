import logging
import os

from dateutil.relativedelta import relativedelta


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


def date_formatter(date_obj, format="iso"):
    if format == "unix":
        return int(date_obj.timestamp())
    else:
        return date_obj.strftime("%Y-%m-%d")


def calculate_expiry_date(today, months=12, format="unix"):
    expiry_date = today + relativedelta(months=+months)
    return date_formatter(expiry_date, format=format)
