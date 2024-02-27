from lambda_functions.v1.tests.conftest import test_constants
from pytest_cases import case

@case(id="Try to validate a code that is valid and active")
def case_validate_valid_code_1():
    test_data = [
        {
            "active": True,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {
        "lpa": "scale_virtual_e_commerce",
        "dob": "1960-06-05",
        "code": "t39hg7zQdE59",
    }

    expected_result = {"actor": "lightcyan"}
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case(id="Try to validate a code that is valid but not active")
def case_validate_valid_code_2():
    test_data = [
        {
            "active": False,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {
        "lpa": "scale_virtual_e_commerce",
        "dob": "1960-06-05",
        "code": "t39hg7zQdE59",
    }

    expected_result = {"actor": None}
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case(id="Try to validate a code that doesn't exist")
def case_validate_non_existent_code():
    test_data = [
        {
            "active": True,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {
        "lpa": "eed4f597-fd87-4536-99d0-895778824861",
        "dob": "1960-06-05",
        "code": "YsSu4iAztUXm",
    }

    expected_result = {"actor": None}
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case(id="Try to validate a code with incorrect dob")
def case_validate_invalid_code_1():
    test_data = [
        {
            "active": True,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {
        "lpa": "scale_virtual_e_commerce",
        "dob": "1960-06-15",
        "code": "t39hg7zQdE59",
    }

    expected_result = {"actor": None}
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case(id="Try to validate a code with incorrect lpa")
def case_validate_invalid_code_2():
    test_data = [
        {
            "active": True,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {"lpa": "not_the_right_lpa", "dob": "1960-06-05", "code": "t39hg7zQdE59"}

    expected_result = {"actor": None}
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case(id="Try to validate a code that is valid and active but past its TTL")
def case_validate_valid_code_3():
    test_data = [
        {
            "active": True,
            "actor": "lightcyan",
            "code": "t39hg7zQdE59",
            "expiry_date": test_constants["EXPIRY_DATE_PAST"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "scale_virtual_e_commerce",
        }
    ]

    data = {
        "lpa": "scale_virtual_e_commerce",
        "dob": "1960-06-05",
        "code": "t39hg7zQdE59",
    }

    expected_result = {"actor": None}
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code
