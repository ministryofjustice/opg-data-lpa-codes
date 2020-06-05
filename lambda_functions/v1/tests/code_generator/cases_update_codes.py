import copy

from pytest_cases import CaseData, case_name, case_tags, cases_generator
from lambda_functions.v1.tests.conftest import test_constants


@case_name("Set multiple existing codes to inactive")
def case_update_multiple_codes_to_inactive() -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "salmon",
            "code": "yEFJH33hn5nX",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "11/11/2019",
            "last_updated_date": "19/06/2020",
            "dob": "1960-06-05",
            "lpa": "streamline_distributed_content",
        },
        {
            "active": False,
            "actor": "salmon",
            "code": "hmeUqZzPniWN",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "10/08/2019",
            "last_updated_date": "08/12/2019",
            "dob": "1960-06-05",
            "lpa": "streamline_distributed_content",
        },
        {
            "active": True,
            "actor": "salmon",
            "code": "XKepiSTiKdzN",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "30/03/2020",
            "last_updated_date": "09/12/2020",
            "dob": "1960-06-05",
            "lpa": "streamline_distributed_content",
        },
    ]

    key = {
        "lpa": "streamline_distributed_content",
        "actor": "salmon",
    }
    code = None

    status = False

    expected_result = 2

    return test_data, key, code, status, expected_result


@case_name("Set multiple existing codes to active")
def case_update_multiple_codes_to_active() -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "royalblue",
            "code": "3XgMCwsiF2h2",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "16/05/2019",
            "last_updated_date": "06/04/2020",
            "dob": "1960-06-05",
            "lpa": "embrace_rich_initiatives",
        },
        {
            "active": False,
            "actor": "royalblue",
            "code": "VbBjr3QRSseU",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "16/03/2020",
            "last_updated_date": "12/05/2020",
            "dob": "1960-06-05",
            "lpa": "embrace_rich_initiatives",
        },
        {
            "active": True,
            "actor": "royalblue",
            "code": "VEzwZXAJu8sU",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "14/03/2020",
            "last_updated_date": "22/10/2020",
            "dob": "1960-06-05",
            "lpa": "embrace_rich_initiatives",
        },
        {
            "active": False,
            "actor": "royalblue",
            "code": "e2vU3JKEzu6Q",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "22/07/2019",
            "last_updated_date": "27/07/2019",
            "dob": "1960-06-05",
            "lpa": "embrace_rich_initiatives",
        },
    ]

    key = {
        "lpa": "embrace_rich_initiatives",
        "actor": "royalblue",
    }
    code = None

    status = True

    expected_result = 2

    return test_data, key, code, status, expected_result


@case_name("Set single existing code to inactive")
def case_update_single_codes_to_inactive() -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "mediumorchid",
            "code": "yhfyAV6yhC7d",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "06/11/2019",
            "last_updated_date": "09/02/2020",
            "dob": "1960-06-05",
            "lpa": "target_bricks_and_clicks_convergence",
        }
    ]

    key = None
    code = "yhfyAV6yhC7d"

    status = False

    expected_result = 1

    return test_data, key, code, status, expected_result


@case_name("Set single existing code to active")
def case_update_single_codes_to_active() -> CaseData:

    test_data = [
        {
            "active": False,
            "actor": "palevioletred",
            "code": "YYK8tX6wKk6K",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "03/04/2020",
            "last_updated_date": "01/03/2021",
            "dob": "1960-06-05",
            "lpa": "revolutionize_out_of_the_box_paradigms",
        }
    ]

    key = None
    code = "YYK8tX6wKk6K"

    status = True

    expected_result = 1

    return test_data, key, code, status, expected_result


@case_name("Set single existing code to active, but it's already active")
def case_update_single_active_codes_to_active() -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "palevioletred",
            "code": "YYK8tX6wKk6K",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "03/04/2020",
            "last_updated_date": "01/03/2021",
            "dob": "1960-06-05",
            "lpa": "revolutionize_out_of_the_box_paradigms",
        }
    ]

    key = None
    code = "YYK8tX6wKk6K"

    status = True

    expected_result = 0

    return test_data, key, code, status, expected_result


@case_name("Set single existing code to inactive, but it's already inactive")
def case_update_single_active_codes_to_active_in233() -> CaseData:

    test_data = [
        {
            "active": False,
            "actor": "palevioletred",
            "code": "YYK8tX6wKk6K",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "03/04/2020",
            "last_updated_date": "01/03/2021",
            "dob": "1960-06-05",
            "lpa": "revolutionize_out_of_the_box_paradigms",
        }
    ]

    key = None
    code = "YYK8tX6wKk6K"

    status = False

    expected_result = 0

    return test_data, key, code, status, expected_result


@case_name("Try to update entries but key doesn't exist")
def case_update_nonexistant_codes_to_active() -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "royalblue",
            "code": "3XgMCwsiF2h2",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "16/05/2019",
            "last_updated_date": "06/04/2020",
            "dob": "1960-06-05",
            "lpa": "embrace_rich_initiatives",
        }
    ]

    key = {
        "lpa": "this_key_does_not_exist",
        "actor": "neither_doess_this_actor",
    }
    code = None

    status = False

    expected_result = 0

    return test_data, key, code, status, expected_result


@case_name("Try to update entries but lpa doesn't exist")
def case_update_nonexistant_codes_to_active_in233_1() -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "royalblue",
            "code": "3XgMCwsiF2h2",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "16/05/2019",
            "last_updated_date": "06/04/2020",
            "dob": "1960-06-05",
            "lpa": "embrace_rich_initiatives",
        }
    ]

    key = {
        "lpa": "this_key_does_not_exist",
        "actor": "royalblue",
    }
    code = None

    status = False

    expected_result = 0

    return test_data, key, code, status, expected_result


@case_name("Try to update entries but actor doesn't exist")
def case_update_nonexistant_codes_to_active_in233_2() -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "royalblue",
            "code": "3XgMCwsiF2h2",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "16/05/2019",
            "last_updated_date": "06/04/2020",
            "dob": "1960-06-05",
            "lpa": "embrace_rich_initiatives",
        }
    ]

    key = {
        "lpa": "embrace_rich_initiatives",
        "actor": "neither_doess_this_actor",
    }
    code = None

    status = False

    expected_result = 0

    return test_data, key, code, status, expected_result


@case_name("Try to update code but code doesn't exist")
def case_update_single_codes_1() -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "mediumorchid",
            "code": "yhfyAV6yhC7d",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "06/11/2019",
            "last_updated_date": "09/02/2020",
            "dob": "1960-06-05",
            "lpa": "target_bricks_and_clicks_convergence",
        }
    ]

    key = None
    code = "I_do_not_exist"

    status = False

    expected_result = 0

    return test_data, key, code, status, expected_result


@cases_generator(
    "Try and update Entries when actor and LPA is blank - {item}", item=["actor", "lpa"]
)
def case_update_multiple_codes_to_inactive_in233(item) -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "salmon",
            "code": "yEFJH33hn5nX",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "11/11/2019",
            "last_updated_date": "19/06/2020",
            "dob": "1960-06-05",
            "lpa": "streamline_distributed_content",
        }
    ]

    default_key = {
        "lpa": "streamline_distributed_content",
        "actor": "salmon",
    }

    key = copy.deepcopy(default_key)
    key[item] = ""

    code = None

    status = False

    expected_result = 0

    return test_data, key, code, status, expected_result


@cases_generator(
    "Try and update Entries when actor and LPA is missing - {item}",
    item=["actor", "lpa"],
)
def case_update_multiple_codes_to_inactive_in233_1(item) -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "salmon",
            "code": "yEFJH33hn5nX",
            "expiry_date": test_constants["EXPIRY_DATE"],
            "generated_date": "11/11/2019",
            "last_updated_date": "19/06/2020",
            "dob": "1960-06-05",
            "lpa": "streamline_distributed_content",
        }
    ]

    default_key = {
        "lpa": "streamline_distributed_content",
        "actor": "salmon",
    }

    key = copy.deepcopy(default_key)
    key.pop(item)

    code = None

    status = False

    expected_result = 0

    return test_data, key, code, status, expected_result
