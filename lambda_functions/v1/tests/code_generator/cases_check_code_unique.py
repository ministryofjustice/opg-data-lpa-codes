from pytest_cases import parametrize_with_cases
from lambda_functions.v1.tests.conftest import test_constants

default_test_data = [
    {
        "active": False,
        "actor": "blueviolet",
        "code": "daNFwFHVHJ9D",
        "expiry_date": test_constants["EXPIRY_DATE"],
        "generated_date": "22/07/2019",
        "last_updated_date": "11/09/2019",
        "dob": "1960-06-05",
        "lpa": "maximize_best_of_breed_synergies",
    },
    {
        "active": True,
        "actor": "blueviolet",
        "code": "zyQ9SWhzmQ9J",
        "expiry_date": test_constants["EXPIRY_DATE"],
        "generated_date": "18/11/2019",
        "last_updated_date": "23/05/2020",
        "dob": "1960-06-05",
        "lpa": "maximize_best_of_breed_synergies",
    },
    {
        "active": True,
        "actor": "blueviolet",
        "code": "meEJZW5i7jrt",
        "expiry_date": test_constants["EXPIRY_DATE"],
        "generated_date": "10/09/2019",
        "last_updated_date": "22/11/2019",
        "dob": "1960-06-05",
        "lpa": "maximize_best_of_breed_synergies",
    },
    {
        "active": False,
        "actor": "blueviolet",
        "code": "jHxG7ctbFizx",
        "expiry_date": test_constants["EXPIRY_DATE"],
        "generated_date": "25/08/2019",
        "last_updated_date": "18/08/2020",
        "dob": "1960-06-05",
        "lpa": "maximize_best_of_breed_synergies",
    },
]


@case(id="Code is unique")
def case_code_is_unique():

    test_data = default_test_data

    code = "t4mjggzeV4LH"
    expected_result = True
    logger_message = "Code does not exist in database"

    return test_data, code, logger_message, expected_result


@case(id="Code is not unique")
def case_code_is_not_unique():

    test_data = default_test_data

    code = "jHxG7ctbFizx"
    expected_result = False
    logger_message = ""

    return test_data, code, logger_message, expected_result
