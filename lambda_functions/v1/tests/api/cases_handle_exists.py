import datetime


from pytest_cases import CaseData, case_name

from lambda_functions.v1.functions.lpa_codes.app.api.helpers import date_formatter
from lambda_functions.v1.tests.conftest import test_constants


@case_name("Check if a code exists for an actor")
def case_actor_code_exists_1() -> CaseData:
    test_data = [
        {
            "active": True,
            "actor": "actor_1",
            "code": "jmABs6fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "lpa_1",
            "status_details": "Generated",
        },
        {
            "active": True,
            "actor": "actor_2",
            "code": "pt4F6fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1966-12-09",
            "lpa": "lpa_1",
            "status_details": "Superseded",
        },
        {
            "active": True,
            "actor": "actor_1",
            "code": "aNe26fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1965-08-21",
            "lpa": "lpa_2",
            "status_details": "Generated",
        },
        {
            "active": False,
            "actor": "actor_1",
            "code": "MYX426fFaNJG",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "2019-09-31",
            "last_updated_date": "2019-12-26",
            "dob": "1960-06-05",
            "lpa": "lpa_1",
            "status_details": "Revoked",
        }
    ]

    data = {
        "lpa": "lpa_1",
        "actor": "actor_1"
    }

    expected_result = {
        "codes": [
            {
                "lpa": "lpa_1",
                "actor": "violet",
                "code": "jmABs6fFaNJG",
                "active": True,
                "generated_date": "2019-09-31",
            },
            {
                "lpa": "lpa_1",
                "actor": "actor_1",
                "code": "MYX426fFaNJG",
                "active": False,
                "generated_date": "2019-09-31",
            }
        ]
    }

    expected_status_code = 200
    return test_data, data, expected_result, expected_status_code

