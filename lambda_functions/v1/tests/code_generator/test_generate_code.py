import logging
import string

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import generate_code


def test_generate_unique_code(mock_unique_code, caplog):

    all_chars = list(string.ascii_letters) + list(string.digits)
    acceptable_chars = list("346789QWERTYUPADFGHJKLXCVBNM")

    unacceptable_characters = [c for c in all_chars if c not in acceptable_chars]

    db = None

    new_codes = []
    for x in range(0, 10):
        print(f"x: {x}")
        code = generate_code(database=db)
        if code is None:
            break
        else:
            new_codes.append(code)

    if len(new_codes) > 0:

        for code in new_codes:
            assert len(code) == 12
            for c in unacceptable_characters:
                assert c not in code

    else:
        with caplog.at_level(logging.ERROR):
            assert (
                "Unable to generate unique code - failed after 10 attempts"
                in caplog.text
            )
