from pytest_cases import CaseData, case_name, case_tags


def by_key_test_data():
    return [
        {
            "active": True,
            "actor": "dodgerblue",
            "code": "r3BpagyjNQYQ",
            "expiry_date": "30/04/2021",
            "generated_date": "30/04/2020",
            "last_updated_date": "19/09/2020",
            "lpa": "syndicate_scalable_relationships",
        },
        {
            "active": True,
            "actor": "dodgerblue",
            "code": "JFumtMCniePa",
            "expiry_date": "06/05/2021",
            "generated_date": "06/05/2020",
            "last_updated_date": "06/01/2021",
            "lpa": "syndicate_scalable_relationships",
        },
        {
            "active": False,
            "actor": "dodgerblue",
            "code": "NwRkYxGSA6BS",
            "expiry_date": "30/01/2021",
            "generated_date": "31/01/2020",
            "last_updated_date": "24/07/2020",
            "lpa": "syndicate_scalable_relationships",
        },
        {
            "active": True,
            "actor": "dodgerblue",
            "code": "7Bxf3JY2cfzj",
            "expiry_date": "10/06/2020",
            "generated_date": "11/06/2019",
            "last_updated_date": "03/01/2020",
            "lpa": "syndicate_scalable_relationships",
        },
        {
            "active": False,
            "actor": "dodgerblue",
            "code": "Wa3dvHTBc8XV",
            "expiry_date": "04/05/2021",
            "generated_date": "04/05/2020",
            "last_updated_date": "17/03/2021",
            "lpa": "syndicate_scalable_relationships",
        },
        {
            "active": False,
            "actor": "dodgerblue",
            "code": "vp7idHyMTGaK",
            "expiry_date": "21/10/2020",
            "generated_date": "22/10/2019",
            "last_updated_date": "29/02/2020",
            "lpa": "syndicate_scalable_relationships",
        },
        {
            "active": False,
            "actor": "dodgerblue",
            "code": "6Rv78c2GdTBH",
            "expiry_date": "31/05/2020",
            "generated_date": "01/06/2019",
            "last_updated_date": "15/03/2020",
            "lpa": "syndicate_scalable_relationships",
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

    test_data = [
        {
            "active": True,
            "actor": "salmon",
            "code": "yEFJH33hn5nX",
            "expiry_date": "10/11/2020",
            "generated_date": "11/11/2019",
            "last_updated_date": "19/06/2020",
            "lpa": "streamline_distributed_content",
        },
        {
            "active": False,
            "actor": "salmon",
            "code": "hmeUqZzPniWN",
            "expiry_date": "09/08/2020",
            "generated_date": "10/08/2019",
            "last_updated_date": "08/12/2019",
            "lpa": "streamline_distributed_content",
        },
        {
            "active": True,
            "actor": "salmon",
            "code": "XKepiSTiKdzN",
            "expiry_date": "30/03/2021",
            "generated_date": "30/03/2020",
            "last_updated_date": "09/12/2020",
            "lpa": "streamline_distributed_content",
        },
    ]

    key = {
        "lpa": "streamline_distributed_content",
        "actor": "salmon",
    }
    code = None

    status = False

    expected_result = "updated"

    return test_data, key, code, status, expected_result


# @case_name("Set code to inactive by code")
# @case_tags("by code")
# def case_update_code_by_code() -> CaseData:
#     code = "hFCarGyJF6G2"
#     status = False
#
#     expected_result = "updated"
#
#     return code, status, expected_result
#
#
# @case_name("Set code to active by code")
# @case_tags("by code")
# def case_update_code_by_code_2() -> CaseData:
#     code = "hFCarGyJF6G2"
#     status = True
#
#     expected_result = "updated"
#
#     return code, status, expected_result
#
#
# @case_name("Set code to inactive by code, but code does not exist")
# @case_tags("by code")
# def case_update_code_by_code_3() -> CaseData:
#     code = "fake_code"
#     status = False
#
#     expected_result = "code does not exist"
#
#     return code, status, expected_result
