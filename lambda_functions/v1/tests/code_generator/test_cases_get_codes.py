from pytest_cases import CaseData, case_name, case_tags


@case_name("Get codes by key")
def case_get_codes_1() -> CaseData:
    code = None
    key = {
        "lpa": "drive_leading-edge_communities",
        "actor": "mediumblue",
    }

    expected_result = code
    expected_result_count = 7
    return code, key, expected_result, expected_result_count


@case_name("Get codes by key that doesn't exist")
def case_get_codes_11() -> CaseData:
    code = None
    key = {
        "lpa": "fake_lpa_id",
        "actor": "fake_actor",
    }

    expected_result = code
    expected_result_count = 0
    return code, key, expected_result, expected_result_count


@case_name("Get codes by code")
def case_get_codes_2() -> CaseData:
    code = "ZY577rXcRVLY"
    key = None

    expected_result = "updated"
    expected_result_count = 1

    return code, key, expected_result, expected_result_count


@case_name("Get codes by code that doesn't exist")
def case_get_codes_21() -> CaseData:
    code = "fake_code"
    key = None

    expected_result = "updated"
    expected_result_count = 0

    return code, key, expected_result, expected_result_count


@case_name("Get codes by both code and key")
def case_get_codes_3() -> CaseData:
    code = "ZY577rXcRVLY"
    key = {
        "lpa": "drive_leading-edge_communities",
        "actor": "mediumblue",
    }

    expected_result = "updated"
    expected_result_count = 1

    return code, key, expected_result, expected_result_count
