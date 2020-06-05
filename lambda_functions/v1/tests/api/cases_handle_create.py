import copy

from pytest_cases import CaseData, case_name, cases_generator

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


@case_name("Create a single code")
def case_create_a_code_1() -> CaseData:
    test_data = copy.deepcopy(default_test_data)

    data = {
        "lpas": [
            {
                "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "dob": "1960-06-05",
            }
        ]
    }

    code = test_constants["DEFAULT_CODE"]

    expected_result = {
        "codes": [
            {
                "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "code": code,
            }
        ]
    }
    return test_data, data, expected_result


@case_name("Create multiple codes")
def case_create_a_code_2() -> CaseData:
    test_data = copy.deepcopy(default_test_data)

    data = {
        "lpas": [
            {
                "actor": "violet_1",
                "dob": "1966-05-21",
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet_2",
                "dob": "1988-11-21",
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet_3",
                "dob": "1969-01-28",
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet_4",
                "dob": "1967-05-11",
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet_5",
                "dob": "1967-12-10",
                "lpa": "productize_out_of_the_box_portals",
            },
        ]
    }

    code = test_constants["DEFAULT_CODE"]

    expected_result = {
        "codes": [
            {
                "actor": "violet_1",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet_2",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet_3",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet_4",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet_5",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
        ]
    }
    return test_data, data, expected_result


@cases_generator(
    "Try and create a code with blank values - {value}", value=["lpa", "actor", "dob"]
)
def case_create_a_code_in233(value) -> CaseData:
    test_data = copy.deepcopy(default_test_data)

    default_data = {
        "lpas": [
            {
                "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "dob": "1960-06-05",
            }
        ]
    }

    data = copy.deepcopy(default_data)
    data["lpas"][0].pop(value)

    print(f"data: {data}")

    expected_result = {"codes": None}
    return test_data, data, expected_result
