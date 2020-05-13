from lambda_functions.v1.functions.lpa_codes.app.api.lets_see_about_this import (
    handle_create,
)


def test_post(mock_database, mock_generate_code):

    data = {
        "lpas": [
            {
                "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                "dob": "1960-06-05",
            }
        ]
    }

    result = handle_create(data=data)

    expected_response = [
        {
            "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
            "code": "idFCGZIvjess",
            "lpa": "eed4f597-fd87-4536-99d0-895778824861",
        }
    ]

    assert result == expected_response
