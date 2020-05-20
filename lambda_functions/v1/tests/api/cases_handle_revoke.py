import datetime
from copy import deepcopy

from pytest_cases import CaseData, case_name, case_tags

from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter


@case_name("Revoke an active code")
def case_revoke_a_code_1() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": "2020-08-30",
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "mesh_end_to_end_systems",
        }
    ]

    data = {
        "code": "jmABs6fFaNJG",
    }

    expected_result = {"codes revoked": 1}
    expected_last_updated_date = date_formatter(date_obj=datetime.datetime.now())
    return test_data, data, expected_result, expected_last_updated_date


@case_name("Revoke an inactive code")
def case_revoke_a_code_2() -> CaseData:
    test_data = [
        {
            "active": False,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": "2020-08-30",
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "mesh_end_to_end_systems",
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
            "expiry_date": "2020-08-30",
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "mesh_end_to_end_systems",
        }
    ]

    data = {
        "code": "not_a_code",
    }

    expected_result = {"codes revoked": 0}
    expected_last_updated_date = "2019-12-26"
    return test_data, data, expected_result, expected_last_updated_date
