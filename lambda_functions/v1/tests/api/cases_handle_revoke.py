import datetime
from copy import deepcopy

from pytest_cases import CaseData, case_name, case_tags


@case_name("Revoke an active code")
def case_revoke_a_code_1() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": "30/08/2020",
            "generated_date": "31/08/2019",
            "last_updated_date": "26/12/2019",
            "lpa": "mesh_end_to_end_systems",
        }
    ]

    data = {
        "code": "jmABs6fFaNJG",
    }

    expected_result = {"codes revoked": 1}
    expected_last_updated_date = datetime.datetime.now().strftime("%d/%m/%Y")
    return test_data, data, expected_result, expected_last_updated_date


@case_name("Revoke an inactive code")
def case_revoke_a_code_2() -> CaseData:
    test_data = [
        {
            "active": False,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": "30/08/2020",
            "generated_date": "31/08/2019",
            "last_updated_date": "26/12/2019",
            "lpa": "mesh_end_to_end_systems",
        }
    ]

    data = {
        "code": "jmABs6fFaNJG",
    }

    expected_result = {"codes revoked": 0}
    expected_last_updated_date = "26/12/2019"
    return test_data, data, expected_result, expected_last_updated_date


@case_name("Try to revoke a code but it doesn't exist")
def case_revoke_a_code_3() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "violet",
            "code": "jmABs6fFaNJG",
            "expiry_date": "30/08/2020",
            "generated_date": "31/08/2019",
            "last_updated_date": "26/12/2019",
            "lpa": "mesh_end_to_end_systems",
        }
    ]

    data = {
        "code": "not_a_code",
    }

    expected_result = {"codes revoked": 0}
    expected_last_updated_date = "26/12/2019"
    return test_data, data, expected_result, expected_last_updated_date
