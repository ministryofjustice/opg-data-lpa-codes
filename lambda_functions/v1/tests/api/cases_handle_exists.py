import datetime


from pytest_cases import CaseData, case_name

from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter
from lambda_functions.v1.tests.conftest import test_constants


@case_name("Check if an active code exists for an actor")
def case_actor_code_exists_1() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "actor_1",
            "code": "jmABs6fFaNJG",
            "dob": "1960-06-05",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_1",
            "generated_date": "2019-09-31",
            "status_details": "Generated",
        },
        {
            "active": True,
            "actor": "actor_2",
            "code": "pt4F6fFaNJG",
            "dob": "1966-12-09",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_1",
            "generated_date": "2019-09-31",
            "status_details": "Superseded",
        },
        {
            "active": True,
            "actor": "actor_1",
            "code": "aNe26fFaNJG",
            "dob": "1965-08-21",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_2",
            "generated_date": "2019-09-31",
            "status_details": "Generated",
        },
        {
            "active": False,
            "actor": "actor_1",
            "code": "MYX426fFaNJG",
            "dob": "1960-06-05",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_1",
            "generated_date": "2019-09-31",
            "status_details": "Revoked",
        }
    ]

    data = {
        "lpa": "lpa_1",
        "actor": "actor_1"
    }

    expected_result = {
        "Created": "2019-09-31"
    }

    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case_name("Returns null if no active codes in query result")
def case_actor_code_exists_2() -> CaseData:
    test_data = [
        {
            "active": False,
            "actor": "actor_1",
            "code": "jmABs6fFaNJG",
            "dob": "1960-06-05",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_1",
            "generated_date": "2019-09-31",
            "status_details": "Revoked",
        },
        {
            "active": False,
            "actor": "actor_1",
            "code": "MYX426fFaNJG",
            "dob": "1960-06-05",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_1",
            "generated_date": "2019-09-31",
            "status_details": "Revoked",
        }
    ]

    data = {
        "lpa": "lpa_1",
        "actor": "actor_1"
    }

    expected_result = {
        "Created": None
    }

    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case_name("Returns null with 200 if no match found")
def case_actor_code_exists_3() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "actor_2",
            "code": "pt4F6fFaNJG",
            "dob": "1966-12-09",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_1",
            "generated_date": "2019-09-31",
            "status_details": "Superseded",
        },
        {
            "active": False,
            "actor": "actor_1",
            "code": "MYX426fFaNJG",
            "dob": "1960-06-05",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_1",
            "generated_date": "2019-09-31",
            "status_details": "Revoked",
        }
    ]

    data = {
        "lpa": "lpa_1",
        "actor": "actor_1"
    }

    expected_result = {
        "Created": None
    }

    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case_name("Returns null with 200 if no match found")
def case_actor_code_exists_4() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "actor_2",
            "code": "pt4F6fFaNJG",
            "dob": "1966-12-09",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_1",
            "generated_date": "2019-09-31",
            "status_details": "Superseded",
        },
        {
            "active": False,
            "actor": "actor_1",
            "code": "MYX426fFaNJG",
            "dob": "1960-06-05",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "last_updated_date": "2019-12-26",
            "lpa": "lpa_1",
            "generated_date": "2019-09-31",
            "status_details": "Revoked",
        }
    ]

    data = {
        "lpa": "lpa_1",
        "actor": "actor_1"
    }

    expected_result = {
        "Created": None
    }

    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code
