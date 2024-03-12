import datetime

from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter
from lambda_functions.v1.tests.conftest import test_constants
from pytest_cases import case


@case(id="Revoke an active code")
def case_revoke_a_code_1():
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

    expected_result = {"codes revoked": 1}
    expected_last_updated_date = test_constants["TODAY_ISO"]
    expected_status_code = 200
    return (
        test_data,
        data,
        expected_result,
        expected_last_updated_date,
        expected_status_code,
    )


@case(id="Revoke a not yet used modernise code")
def case_revoke_a_not_yet_used_modernise_code():
    test_data = [
        {
            "active": True,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "M-3AC4-1274-AP1H",
            "status_details": "Generated",
        }
    ]

    data = {
        "code": "jmABs6fFaNJG",
    }

    expected_result = {"codes revoked": 1}
    expected_last_updated_date = test_constants["TODAY_ISO"]
    expected_status_code = 200
    return (
        test_data,
        data,
        expected_result,
        expected_last_updated_date,
        expected_status_code,
    )


@case(id="Revoke an inactive code")
def case_revoke_a_code_2():
    test_data = [
        {
            "active": False,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "700000000096",
            "status_details": "Superseded",
        }
    ]

    data = {
        "code": "jmABs6fFaNJG",
    }

    expected_result = {"codes revoked": 0}
    expected_last_updated_date = "2019-12-26"
    expected_status_code = 200
    return (
        test_data,
        data,
        expected_result,
        expected_last_updated_date,
        expected_status_code,
    )


@case(id="Try to revoke a code but it doesn't exist")
def case_revoke_a_code_3():
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
            "status_details": "Revoked",
        }
    ]

    data = {
        "code": "not_a_code",
    }

    expected_result = {"codes revoked": 0}
    expected_last_updated_date = "2019-12-26"
    expected_status_code = 200
    return (
        test_data,
        data,
        expected_result,
        expected_last_updated_date,
        expected_status_code,
    )
