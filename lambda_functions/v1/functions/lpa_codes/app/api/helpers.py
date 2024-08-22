import logging
import os

from dateutil.relativedelta import relativedelta


def custom_logger(name=None):
    """
    For consistent logger message formatting

    Args:
        name: string

    Returns:
        Logger instance
    """
    logger_name = name if name else "lpa_code_generator"
    formatter = logging.Formatter(
        fmt=f"%(asctime)s - %(levelname)s - {logger_name} - in %("
        f"funcName)s:%(lineno)d - %(message)s"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.propagate = False

    try:
        logger.setLevel(os.environ["LOGGER_LEVEL"])
    except KeyError:
        logger.setLevel("INFO")
    logger.addHandler(handler)
    return logger


def date_formatter(date_obj, format="iso"):
    """
    All human-readable dates inserted into db table should be in a consistent (ISO)
    format.
    TTL needs to be in unix time

    Args:
        date_obj: date that needs formatting
        format: string, iso or unix

    Returns:
        formatted date, either string or int
    """
    if format == "unix":
        return int(date_obj.timestamp())
    else:
        return date_obj.strftime("%Y-%m-%d")


def calculate_expiry_date(today, months=12, format="unix"):
    """
    Calculates the expiry date of the code and formats to unix timestamp
    Args:
        today: date object
        months: int
        format: string

    Returns:
        formatted expiry date
    """
    expiry_date = today + relativedelta(months=+months)
    return date_formatter(expiry_date, format=format)
