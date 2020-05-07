from pytest_cases import CaseData, case_name, case_tags


@case_name("Set multiple existing codes to inactive")
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

    expected_result = 2

    return test_data, key, code, status, expected_result


@case_name("Set multiple existing codes to active")
def case_update_multiple_codes_to_active() -> CaseData:

    test_data = [
        {
            "active": True,
            "actor": "royalblue",
            "code": "3XgMCwsiF2h2",
            "expiry_date": "15/05/2020",
            "generated_date": "16/05/2019",
            "last_updated_date": "06/04/2020",
            "lpa": "embrace_rich_initiatives",
        },
        {
            "active": False,
            "actor": "royalblue",
            "code": "VbBjr3QRSseU",
            "expiry_date": "16/03/2021",
            "generated_date": "16/03/2020",
            "last_updated_date": "12/05/2020",
            "lpa": "embrace_rich_initiatives",
        },
        {
            "active": True,
            "actor": "royalblue",
            "code": "VEzwZXAJu8sU",
            "expiry_date": "14/03/2021",
            "generated_date": "14/03/2020",
            "last_updated_date": "22/10/2020",
            "lpa": "embrace_rich_initiatives",
        },
        {
            "active": False,
            "actor": "royalblue",
            "code": "e2vU3JKEzu6Q",
            "expiry_date": "21/07/2020",
            "generated_date": "22/07/2019",
            "last_updated_date": "27/07/2019",
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
            "expiry_date": "05/11/2020",
            "generated_date": "06/11/2019",
            "last_updated_date": "09/02/2020",
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
            "expiry_date": "03/04/2021",
            "generated_date": "03/04/2020",
            "last_updated_date": "01/03/2021",
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
            "expiry_date": "03/04/2021",
            "generated_date": "03/04/2020",
            "last_updated_date": "01/03/2021",
            "lpa": "revolutionize_out_of_the_box_paradigms",
        }
    ]

    key = None
    code = "YYK8tX6wKk6K"

    status = True

    expected_result = 0

    return test_data, key, code, status, expected_result
