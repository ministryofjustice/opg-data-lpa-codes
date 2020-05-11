from copy import deepcopy

from pytest_cases import CaseData, case_name, case_tags

default_test_data = [
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
    {
        "active": False,
        "actor": "mediumblue",
        "code": "hm8Qtyb763tD",
        "expiry_date": "05/08/2020",
        "generated_date": "06/08/2019",
        "last_updated_date": "01/12/2019",
        "lpa": "drive_leading-edge_communities",
    },
    {
        "active": False,
        "actor": "mediumblue",
        "code": "HiRqUNXRKB3X",
        "expiry_date": "02/01/2021",
        "generated_date": "03/01/2020",
        "last_updated_date": "11/04/2020",
        "lpa": "drive_leading-edge_communities",
    },
    {
        "active": False,
        "actor": "mediumblue",
        "code": "UEW7zSi42bLF",
        "expiry_date": "09/03/2021",
        "generated_date": "09/03/2020",
        "last_updated_date": "17/10/2020",
        "lpa": "drive_leading-edge_communities",
    },
]


@case_name("Get codes by key")
def case_get_codes_1() -> CaseData:
    test_data = deepcopy(default_test_data)
    code = None
    key = {
        "lpa": "drive_leading-edge_communities",
        "actor": "mediumblue",
    }

    expected_result = code
    expected_result_count = 7
    return test_data, code, key, expected_result, expected_result_count


@case_name("Get codes by key that doesn't exist")
def case_get_codes_11() -> CaseData:
    test_data = deepcopy(default_test_data)
    code = None
    key = {
        "lpa": "fake_lpa_id",
        "actor": "fake_actor",
    }

    expected_result = None
    expected_result_count = 0
    return test_data, code, key, expected_result, expected_result_count


@case_name("Get codes by code")
def case_get_codes_2() -> CaseData:
    test_data = deepcopy(default_test_data)
    code = "ZY577rXcRVLY"
    key = None

    expected_result = code
    expected_result_count = 1

    return test_data, code, key, expected_result, expected_result_count


@case_name("Get codes by code that doesn't exist")
def case_get_codes_21() -> CaseData:
    test_data = deepcopy(default_test_data)
    code = "fake_code"
    key = None

    expected_result = None
    expected_result_count = 0

    return test_data, code, key, expected_result, expected_result_count


@case_name("Get codes by both code and key")
def case_get_codes_3() -> CaseData:
    test_data = deepcopy(default_test_data)
    code = "ZY577rXcRVLY"
    key = {
        "lpa": "drive_leading-edge_communities",
        "actor": "mediumblue",
    }

    expected_result = code
    expected_result_count = 1

    return test_data, code, key, expected_result, expected_result_count
