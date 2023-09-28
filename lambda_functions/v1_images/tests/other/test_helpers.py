from lambda_functions.v1.functions.lpa_codes.app.api.helpers import (
    date_formatter,
    calculate_expiry_date,
    custom_logger,
)
import datetime


def test_date_formatter():
    test_date = datetime.datetime(
        year=2020,
        month=5,
        day=26,
        hour=10,
        minute=0,
        second=0,
        tzinfo=datetime.timezone.utc,
    )

    date = date_formatter(test_date, format="iso")

    assert date == "2020-05-26"

    date = date_formatter(test_date, format="unix")

    assert date == 1590487200


def test_calculate_expiry_date():
    test_date = datetime.datetime(
        year=2020,
        month=5,
        day=26,
        hour=10,
        minute=0,
        second=0,
        tzinfo=datetime.timezone.utc,
    )

    expiry_date = calculate_expiry_date(today=test_date, months=12, format="unix")

    assert expiry_date == 1622023200

    expiry_date = calculate_expiry_date(today=test_date, months=12, format="iso")

    assert expiry_date == "2021-05-26"

    expiry_date = calculate_expiry_date(today=test_date, months=1, format="iso")

    assert expiry_date == "2020-06-26"


def test_custom_logger(monkeypatch):

    monkeypatch.delenv("LOGGER_LEVEL")
    logger = custom_logger()

    assert logger.level == 20
