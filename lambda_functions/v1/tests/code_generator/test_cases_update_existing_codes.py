from pytest_cases import CaseData, case_name


@case_name("Set existing key to inactive")
def case_update_single_code_to_inactive() -> CaseData:
    keys = [
        {
            "lpa": "drive_leading-edge_communities",
            "actor": "mediumblue",
            "code": "YsSu4iAztUXm",
        }
    ]
    status = False
    active_codes = 1

    expected_result = "updated"

    return keys, active_codes, status, expected_result


@case_name("Set multiple existing key to inactive")
def case_update_multiple_codes_to_inactive() -> CaseData:
    keys = [
        {
            "lpa": "drive_leading-edge_communities",
            "actor": "mediumblue",
            "code": "ZY577rXcRVLY",
        },
        {
            "lpa": "drive_leading-edge_communities",
            "actor": "mediumblue",
            "code": "aEYVS6i9zSwy",
        },
        {
            "lpa": "drive_leading-edge_communities",
            "actor": "mediumblue",
            "code": "hFCarGyJF6G2",
        },
    ]
    status = False
    active_codes = 2

    expected_result = "updated"

    return keys, active_codes, status, expected_result
