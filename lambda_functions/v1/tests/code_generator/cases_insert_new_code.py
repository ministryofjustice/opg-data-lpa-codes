import datetime

from pytest_cases import CaseData


def case_insert_a_code() -> CaseData:
    key = {
        "lpa": "f2dcb20f-b5d7-4c5e-8164-0408ea033a31",
        "actor": "6f41cde2-f5f2-45d9-8776-e6dcdb1b56e8",
    }

    code = "2gVYdRNjUHTX"

    expected_result = [
        {
            "lpa": "f2dcb20f-b5d7-4c5e-8164-0408ea033a31",
            "actor": "6f41cde2-f5f2-45d9-8776-e6dcdb1b56e8",
            "code": "2gVYdRNjUHTX",
            "active": True,
            "last_updated_date": datetime.datetime.now().strftime("%d/%m/%Y"),
        }
    ]

    return key, code, expected_result