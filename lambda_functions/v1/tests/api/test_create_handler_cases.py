import copy

from lambda_functions.v1.tests.conftest import test_constants
from pytest_cases import case

default_test_data = [
    {
        "lpa": "700000000092",
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
        "lpa": "700000000092",
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
        "lpa": "M-3AF4-1274-A81H",
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
        "lpa": "M-3AF4-1274-A81H",
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


@case(id="Create a single code")
def case_create_a_code_1():
    test_data = copy.deepcopy(default_test_data)

    data = {
        "lpas": [
            {
                "lpa": "700000000092",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "dob": "1960-06-05",
            }
        ]
    }

    code = test_constants["DEFAULT_CODE"]

    expected_result = {
        "codes": [
            {
                "lpa": "700000000092",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "code": code,
            }
        ]
    }
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code


@case(id="Create a single Modernise code")
def case_create_a_modernise_code():
    test_data = copy.deepcopy(default_test_data)

    data = {
        "lpas": [
            {
                "lpa": "M-3AF4-1274-A81H",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "dob": "1960-06-05",
            }
        ]
    }

    code = test_constants["DEFAULT_CODE"]

    expected_result = {
        "codes": [
            {
                "lpa": "M-3AF4-1274-A81H",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "code": code,
            }
        ]
    }
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code

@case(id="Create multiple codes")
def case_create_a_code_2():
    test_data = copy.deepcopy(default_test_data)

    data = {
        "lpas": [
            {
                "actor": "violet_1",
                "dob": "1966-05-21",
                "lpa": "M-3AF4-1274-A81H",
            },
            {
                "actor": "violet_2",
                "dob": "1988-11-21",
                "lpa": "M-3AF4-1274-A81H",
            },
            {
                "actor": "violet_3",
                "dob": "1969-01-28",
                "lpa": "M-3AF4-1274-A81H",
            },
            {
                "actor": "violet_4",
                "dob": "1967-05-11",
                "lpa": "M-3AF4-1274-A81H",
            },
            {
                "actor": "violet_5",
                "dob": "1967-12-10",
                "lpa": "M-3AF4-1274-A81H",
            },
        ]
    }

    code = test_constants["DEFAULT_CODE"]

    expected_result = {
        "codes": [
            {
                "actor": "violet_1",
                "code": code,
                "lpa": "M-3AF4-1274-A81H",
            },
            {
                "actor": "violet_2",
                "code": code,
                "lpa": "M-3AF4-1274-A81H",
            },
            {
                "actor": "violet_3",
                "code": code,
                "lpa": "M-3AF4-1274-A81H",
            },
            {
                "actor": "violet_4",
                "code": code,
                "lpa": "M-3AF4-1274-A81H",
            },
            {
                "actor": "violet_5",
                "code": code,
                "lpa": "M-3AF4-1274-A81H",
            },
        ]
    }
    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code
