from pytest_cases import CaseData, case_name


@case_name("Create a single code")
def case_create_a_code_1() -> CaseData:

    data = {
        "lpas": [
            {
                "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "dob": "1960-06-05",
            }
        ]
    }

    code = "tOhkrldOqewm"

    expected_result = {
        "codes": [
            {
                "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "code": code,
            }
        ]
    }
    return data, expected_result


@case_name("Create multiple codes")
def case_create_a_code_2() -> CaseData:

    data = {
        "lpas": [
            {
                "actor": "violet",
                "dob": "1966-05-21",
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet",
                "dob": "1988-11-21",
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet",
                "dob": "1969-01-28",
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet",
                "dob": "1967-05-11",
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet",
                "dob": "1967-12-10",
                "lpa": "productize_out_of_the_box_portals",
            },
        ]
    }

    code = "tOhkrldOqewm"

    expected_result = {
        "codes": [
            {
                "actor": "violet",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
            {
                "actor": "violet",
                "code": code,
                "lpa": "productize_out_of_the_box_portals",
            },
        ]
    }
    return data, expected_result
