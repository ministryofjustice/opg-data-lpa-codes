import datetime

from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter
from lambda_functions.v1.tests.conftest import test_constants
from pytest_cases import case
from test_mark_used_handler import two_years_from_now


@case(id="Mark a code as used")
def case_mark_a_code_as_used():
    test_data = [
        {
            "active": True,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "700000000096",
            "status_details": "Generated",
        }
    ]

    data = {
        "code": "jmABs6fFaNJG",
    }

    expected_result = {"codes marked used": 1}
    expected_last_updated_date = test_constants["TODAY_ISO"]
    expected_status_code = 200
    expected_expiry_date = two_years_from_now
    return (
        test_data,
        data,
        expected_result,
        expected_last_updated_date,
        expected_expiry_date,
    )

@case(id="Try to mark a code as used but it doesn't exist")
def case_mark_a_code_as_used_but_does_not_exist():
    test_data = [
        {
            "active": True,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "700000000096",
            "status_details": "Generated",
        }
    ]

    data = {
        "code": "not_a_code",
    }

    expected_result = {"codes marked used": 0}
    expected_last_updated_date = "2019-12-26"
    expected_status_code = 200
    return (
        test_data,
        data,
        expected_result,
        expected_last_updated_date,
        expected_status_code,
    )
