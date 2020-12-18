from werkzeug.exceptions import abort

from . import code_generator
from .database import db_connection
from .helpers import custom_logger


logger = custom_logger()


def handle_create(data):
    """
    For each lpa/actor/dob compbo provided by the consumer we:
        1. revoke any existing codes for that key (lpa/actor)
        2. generate a new code
        3. insert that new code, key and dob into the database

    Combine all new codes into a list to return to the consumer

    Args:
        data: dict of payload data

    Example args:
        {
          "lpas": [
            {
              "lpa": "eed4f597-fd87-4536-99d0-895778824861",
              "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
              "dob": "1960-06-05"
            },
            {
              "lpa": "eed4f597-fd87-4536-99d0-895778824861",
              "actor": "9a619d46-8712-4bfb-a49f-c14914ff319d",
              "dob": "1983-08-20"
            }
          ]
        }

    Returns:
        tuple: (created codes, http status code)

    Example return:
    (
        {"codes": [
                {
                "lpa": "568c6b37-46ed-44e6-a579-2d82f0504ef4",
                "actor":"9085ada2-d76f-41f8-a2d9-bea404ce90ac",
                "code": "euPtayQAvDqL"
                }
            ]
        },
        200
    )
    """

    db = db_connection()

    code_list = []

    for entry in data["lpas"]:
        lpa = entry["lpa"]
        actor = entry["actor"]
        dob = entry["dob"]

        key = {"lpa": lpa, "actor": actor}

        # 1. expire all existing codes for LPA/Actor combo
        try:
            code_generator.update_codes(
                database=db, key=key, status=False, status_details="Superseded"
            )
        except Exception as e:
            logger.error(f"Error in handle_create > get_codes: {e}")
            return None, 500

        # 2. generate a new code
        try:
            generated_code = code_generator.generate_code(database=db)
        except Exception as e:
            logger.error(f"Error in handle_create > generate_code: {e}")
            return None, 500

        # 3. insert new code into database
        try:
            new_code = code_generator.insert_new_code(
                database=db, key=key, dob=dob, code=generated_code
            )[0]["code"]
        except Exception as e:
            logger.error(f"Error in handle_create > insert_new_code: {e}")
            return None, 500

        # 4. return the new code in lambda payload
        response = {
            "lpa": entry["lpa"],
            "actor": entry["actor"],
            "code": new_code,
        }

        code_list.append(response)
        logger.info(f"code_list: {code_list}")

    return {"codes": code_list}, 200


def handle_revoke(data):
    """
    Updates the status of the provided code to inactive, updates the details to
    "Revoked".
    Returns the number of codes revoked - this should always be 1 as there should
    never be duplicated codes

    Args:
        data: dict of payload data

    Example args:
        {
          "code": "YsSu4iAztUXm"
        }

    Returns:
        tuple: (number of codes revoked, http status code)

    Example return:
        (
            {"codes revoked": 1},
            200
        )

    """
    db = db_connection()

    try:
        update_result = code_generator.update_codes(
            database=db, code=data["code"], status_details="Revoked"
        )
    except Exception as e:
        logger.error(f"Error in handle_revoke > update_codes: {e}")
        return None, 500

    return {"codes revoked": update_result}, 200


def handle_validate(data):
    """
    Validates the combination of lpa/dob/code is active and valid:
        1. try and find the code in the database
        2. if the code exists, check the given dob & lpa match the values in the db
        for that code and check the status is active
        3. if they don't match/not active, return None for the actor

    Args:
        data: dict of payload data

    Example args:
        {
          "lpa": "eed4f597-fd87-4536-99d0-895778824861",
          "dob": "1960-06-05",
          "code": "YsSu4iAztUXm"
        }

    Returns:
        tuple: (actor identifier, http status code)

    Example return:
        (
            {"actor": "a95a0543-6e9e-4fd5-9c77-94eb1a8f4da6"},
            200
        )

    """
    db = db_connection()
    code_to_test = data["code"]

    try:
        code_details = code_generator.get_codes(database=db, code=code_to_test)
    except Exception as e:
        logger.error(f"Error in handle_validate > get_codes: {e}")
        return None, 500

    if len(code_details) != 1:
        return {"actor": None}, 200

    data["active"] = True
    test_code_details = data

    valid_code_details = {
        "code": code_details[0]["code"],
        "dob": code_details[0]["dob"],
        "lpa": code_details[0]["lpa"],
        "active": code_details[0]["active"],
    }

    if dict(sorted(test_code_details.items())) == dict(
        sorted(valid_code_details.items())
    ):
        return {"actor": code_details[0]["actor"]}, 200
    else:
        return {"actor": None}, 200


def handle_check_actor_has_code(data):
    """
    Args:
        data: dict of payload data

    Example args:
        {
            "lpa": "568c6b37-46ed-44e6-a579-2d82f0504ef4",
            "actor":"9085ada2-d76f-41f8-a2d9-bea404ce90ac",
        }

    Returns:
        tuple: (matched codes, http status code)

    Example return:
    (
        {"codes": [
                {
                    "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                    "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                    "code": "euPtayQAvDqL",
                    "active": True,
                    "generated_date": "2020-01-01",
                },
                {
                    "lpa": "eed4f597-fd87-4536-99d0-895778824861",
                    "actor": "12ad81a9-f89d-4804-99f5-7c0c8669ac9b",
                    "code": "kpDHIFRahjk",
                    "active": True,
                    "generated_date": "2020-01-02",
                },
            ]
        },
        200
    )
    """

    db = db_connection()

    lpa = data["lpa"]
    actor = data["actor"]

    key = {"lpa": lpa, "actor": actor}

    try:
        code_details = code_generator.get_codes(database=db, key=key)
    except Exception as e:
        logger.error(f"Error in handle_check_actor_has_code > get_codes: {e}")
        return None, 500

    test_code_details = data

    if code_details:

        return {"codes": code_details}, 200

    else:
        return {"codes": None}, 200


