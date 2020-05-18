import datetime
from copy import deepcopy

from pytest_cases import CaseData, case_name, case_tags


@case_name("Create a single code")
def case_create_a_code_1() -> CaseData:

    data = {
        "lpas": [
            {
                "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "dob": "1960-06-05",
            }
        ]
    }

    expected_result = {
        "codes": [
            {
                "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "code": "idFCGZIvjess",
            }
        ]
    }
    return data, expected_result
