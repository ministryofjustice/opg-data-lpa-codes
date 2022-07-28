import copy

from pytest_cases import CaseData, case_name

from lambda_functions.v1.tests.conftest import test_constants

default_test_data = [
    {
        "lpa": "eed4f597-fd87-4536-99d0-895778824861",
        "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
        "code": "code_1",
        "active": True,
        "last_updated_date": "2020-01-01",
        "dob": "1960-06-05",
        "generated_date": "2020-01-01",
        "expiry_date": test_constants["EXPIRY_DATE"],
        "status_details": "Generated",
    },
    {
        "lpa": "eed4f597-fd87-4536-99d0-895778824861",
        "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
        "code": "code_2",
        "active": True,
        "last_updated_date": "2020-01-02",
        "dob": "1960-06-05",
        "generated_date": "2020-01-02",
        "expiry_date": test_constants["EXPIRY_DATE"],
        "status_details": "Generated",
    },
    {
        "lpa": "productize_out_of_the_box_portals",
        "actor": "violet",
        "code": "code_3",
        "active": True,
        "last_updated_date": "2020-01-01",
        "dob": "1960-06-05",
        "generated_date": "2020-01-01",
        "expiry_date": test_constants["EXPIRY_DATE"],
        "status_details": "Generated",
    },
    {
        "lpa": "productize_out_of_the_box_portals",
        "actor": "violet",
        "code": "code_4",
        "active": True,
        "last_updated_date": "2020-01-02",
        "dob": "1960-06-05",
        "generated_date": "2020-01-02",
        "expiry_date": test_constants["EXPIRY_DATE"],
        "status_details": "Generated",
    },
]


@case_name("Get a single code")
def case_get_a_code_1() -> CaseData:
    test_data = copy.deepcopy(default_test_data)

    data = {
        "code": "code_1"
    }

    expected_result = [default_test_data[0]]
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case_name("404 when code not found")
def case_get_a_code_2() -> CaseData:
    test_data = copy.deepcopy(default_test_data)

    data = {
        "code": "abcdefg"
    }

    expected_result = None
    expected_status_code = 404
    return test_data, data, expected_result, expected_status_code
