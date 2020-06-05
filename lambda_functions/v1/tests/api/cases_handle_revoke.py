import datetime


from pytest_cases import CaseData, case_name

from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter
from lambda_functions.v1.tests.conftest import test_constants


@case_name("Revoke an active code")
def case_revoke_a_code_1() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "mesh_end_to_end_systems",
            "status_details": "Generated",
        }
    ]

    data = {
        "code": "jmABs6fFaNJG",
    }

    expected_result = {"codes revoked": 1}
    expected_last_updated_date = test_constants["TODAY_ISO"]
    return test_data, data, expected_result, expected_last_updated_date


@case_name("Revoke an inactive code")
def case_revoke_a_code_2() -> CaseData:
    test_data = [
        {
            "active": False,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "mesh_end_to_end_systems",
            "status_details": "Superseded",
        }
    ]

    data = {
        "code": "jmABs6fFaNJG",
    }

    expected_result = {"codes revoked": 0}
    expected_last_updated_date = "2019-12-26"
    return test_data, data, expected_result, expected_last_updated_date


@case_name("Try to revoke a code but it doesn't exist")
def case_revoke_a_code_3() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "mesh_end_to_end_systems",
            "status_details": "Revoked",
        }
    ]

    data = {
        "code": "not_a_code",
    }

    expected_result = {"codes revoked": 0}
    expected_last_updated_date = "2019-12-26"
    return test_data, data, expected_result, expected_last_updated_date


@case_name("Revoke a code by sending empty string")
def case_revoke_a_code_in233() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "mesh_end_to_end_systems",
            "status_details": "Generated",
        }
    ]

    data = {
        "code": "",
    }

    expected_result = {"codes revoked": 0}
    expected_last_updated_date = test_constants["TODAY_ISO"]
    return test_data, data, expected_result, expected_last_updated_date
