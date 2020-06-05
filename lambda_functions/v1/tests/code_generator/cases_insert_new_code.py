from decimal import Decimal

from pytest_cases import CaseData

from lambda_functions.v1.tests.conftest import test_constants


def case_insert_a_code() -> CaseData:
    key = {
        "lpa": "f2dcb20f-b5d7-4c5e-8164-0408ea033a31",
        "actor": "6f41cde2-f5f2-45d9-8776-e6dcdb1b56e8",
    }
    dob = "1960-06-05"
    code = "2gVYdRNjUHTX"

    expected_result = [
        {
            "lpa": "f2dcb20f-b5d7-4c5e-8164-0408ea033a31",
            "actor": "6f41cde2-f5f2-45d9-8776-e6dcdb1b56e8",
            "code": "2gVYdRNjUHTX",
            "active": True,
            "last_updated_date": test_constants["TODAY_ISO"],
            "dob": "1960-06-05",
            "expiry_date": test_constants["EXPIRY_DATE"],
        }
    ]

    expected_row = {
        "lpa": "f2dcb20f-b5d7-4c5e-8164-0408ea033a31",
        "actor": "6f41cde2-f5f2-45d9-8776-e6dcdb1b56e8",
        "code": "2gVYdRNjUHTX",
        "active": True,
        "last_updated_date": test_constants["TODAY_ISO"],
        "dob": "1960-06-05",
        "expiry_date": test_constants["EXPIRY_DATE"],
        "generated_date": test_constants["TODAY_ISO"],
        "status_details": "Generated",
    }

    return key, code, dob, expected_result, expected_row
