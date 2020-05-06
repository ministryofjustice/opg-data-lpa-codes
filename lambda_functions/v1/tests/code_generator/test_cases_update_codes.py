from pytest_cases import CaseData, case_name, case_tags


def by_key_test_data():
    return [
        {
            "active": True,
            "actor": "mediumblue",
            "code": "YsSu4iAztUXm",
            "expiry_date": "29/03/2021",
            "generated_date": "29/03/2020",
            "last_updated_date": "25/08/2020",
            "lpa": "drive_leading-edge_communities",
        },
        {
            "active": True,
            "actor": "mediumblue",
            "code": "aEYVS6i9zSwy",
            "expiry_date": "26/06/2020",
            "generated_date": "27/06/2019",
            "last_updated_date": "03/02/2020",
            "lpa": "drive_leading-edge_communities",
        },
        {
            "active": True,
            "actor": "mediumblue",
            "code": "ZY577rXcRVLY",
            "expiry_date": "05/04/2021",
            "generated_date": "05/04/2020",
            "last_updated_date": "28/02/2021",
            "lpa": "drive_leading-edge_communities",
        },
        {
            "active": False,
            "actor": "mediumblue",
            "code": "hFCarGyJF6G2",
            "expiry_date": "06/08/2020",
            "generated_date": "07/08/2019",
            "last_updated_date": "24/03/2020",
            "lpa": "drive_leading-edge_communities",
        },
    ]


# @case_name("Set existing code to inactive")
# @case_tags("by key")
# def case_update_single_code_to_inactive() -> CaseData:
#     keys = [
#         {
#             "lpa": "drive_leading-edge_communities",
#             "actor": "mediumblue",
#             # "code": "YsSu4iAztUXm",
#         }
#     ]
#     status = False
#     active_codes = 1
#
#     expected_result = "updated"
#
#     return keys, active_codes, status, expected_result


@case_name("Set multiple existing codes to inactive")
@case_tags("by key")
def case_update_multiple_codes_to_inactive() -> CaseData:
    key = {
        "lpa": "drive_leading-edge_communities",
        "actor": "mediumblue",
        # "code": "ZY577rXcRVLY",
    }

    status = False
    active_codes = 3

    expected_result = "updated"

    return key, active_codes, status, expected_result


@case_name("Set code to inactive by code")
@case_tags("by code")
def case_update_code_by_code() -> CaseData:
    code = "YsSu4iAztUXm"
    status = False

    expected_result = "updated"

    return code, status, expected_result


@case_name("Set code to active by code")
@case_tags("by code")
def case_update_code_by_code_2() -> CaseData:
    code = "hFCarGyJF6G2"
    status = True

    expected_result = "updated"

    return code, status, expected_result


@case_name("Set code to inactive by code, but code does not exist")
@case_tags("by code")
def case_update_code_by_code_3() -> CaseData:
    code = "fake_code"
    status = False

    expected_result = "code does not exist"

    return code, status, expected_result
