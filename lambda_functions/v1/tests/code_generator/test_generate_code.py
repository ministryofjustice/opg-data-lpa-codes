import logging

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import generate_code


def test_generate_code(mock_unique_code, caplog):
    unacceptable_characters = ["1", "0", "l", "o", "I", "O"]

    new_code = generate_code()

    if new_code is not None:
        assert len(new_code) == 12
        for c in unacceptable_characters:
            assert c not in new_code
    else:
        with caplog.at_level(logging.ERROR):
            assert (
                "Unable to generate unique code - failed after 10 attempts"
                in caplog.text
            )
