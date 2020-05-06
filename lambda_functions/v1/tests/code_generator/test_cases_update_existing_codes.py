from pytest_cases import CaseData, case_name


@case_name("Set existing key to inactive, with no status change")
def case_update_single_code_to_inactive() -> CaseData:
    keys = [
        {
            "lpa": "b53152a3-9973-44dc-83a2-9ef2e89a14e3",
            "actor": "28d13ef6-b7f2-45fd-b97c-e2d7008eb0bd",
            "code": "uEVRMn7gAwDC",
        }
    ]
    status = False

    expected_result = "updated"

    return keys, status, expected_result
