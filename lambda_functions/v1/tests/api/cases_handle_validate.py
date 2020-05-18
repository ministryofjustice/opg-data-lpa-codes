from copy import deepcopy

from pytest_cases import CaseData, case_name, case_tags


@case_name("Try to validate a code that is valid and active")
def case_validate_valid_code_1() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": "19/10/2020",
            "generated_date": "20/10/2019",
            "dob": "1960-06-05",
            "last_updated_date": "26/10/2019",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {
        "lpa": "scale_virtual_e_commerce",
        "dob": "1960-06-05",
        "code": "t39hg7zQdE59",
    }

    expected_result = (True, "lightcyan")
    return test_data, data, expected_result


@case_name("Try to validate a code that is valid but not active")
def case_validate_valid_code_2() -> CaseData:
    test_data = [
        {
            "active": False,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": "19/10/2020",
            "generated_date": "20/10/2019",
            "dob": "1960-06-05",
            "last_updated_date": "26/10/2019",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {
        "lpa": "scale_virtual_e_commerce",
        "dob": "1960-06-05",
        "code": "t39hg7zQdE59",
    }

    expected_result = (False, None)
    return test_data, data, expected_result


@case_name("Try to validate a code that doesn't exist")
def case_validate_non_existent_code() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": "19/10/2020",
            "generated_date": "20/10/2019",
            "last_updated_date": "26/10/2019",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {
        "lpa": "eed4f597-fd87-4536-99d0-895778824861",
        "dob": "1960-06-05",
        "code": "YsSu4iAztUXm",
    }

    expected_result = (False, None)
    return test_data, data, expected_result


@case_name("Try to validate a code with incorrect dob")
def case_validate_invalid_code_1() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": "19/10/2020",
            "generated_date": "20/10/2019",
            "dob": "1960-06-05",
            "last_updated_date": "26/10/2019",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {
        "lpa": "scale_virtual_e_commerce",
        "dob": "1960-06-15",
        "code": "t39hg7zQdE59",
    }

    expected_result = (False, None)
    return test_data, data, expected_result


@case_name("Try to validate a code with incorrect lpa")
def case_validate_invalid_code_2() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": "19/10/2020",
            "generated_date": "20/10/2019",
            "dob": "1960-06-05",
            "last_updated_date": "26/10/2019",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {"lpa": "not_the_right_lpa", "dob": "1960-06-05", "code": "t39hg7zQdE59"}

    expected_result = (False, None)
    return test_data, data, expected_result
