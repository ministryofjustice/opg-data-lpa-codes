from . import code_generator
from .database import db_connection
from .helpers import custom_logger


logger = custom_logger()


def handle_create(data):
    """
    Placeholder for create a code endpoint
    Returns:
    json
    """

    db = db_connection()

    code_list = []

    for entry in data["lpas"]:

        try:
            lpa = entry["lpa"]
            actor = entry["actor"]
            dob = entry["dob"]

            key = {"lpa": lpa, "actor": actor}

            # 1. expire all existing codes for LPA/Actor combo
            code_generator.update_codes(
                database=db, key=key, status=False, status_details="Superseded"
            )

            # 2. generate a new code
            generated_code = code_generator.generate_code(database=db)

            # 3. insert new code into database
            new_code = code_generator.insert_new_code(
                database=db, key=key, dob=dob, code=generated_code
            )[0]["code"]

            # 4. return the new code in lambda payload
            response = {
                "lpa": entry["lpa"],
                "actor": entry["actor"],
                "code": new_code,
            }

            code_list.append(response)
            logger.info(f"code_list: {code_list}")
        except KeyError:
            return {"codes": None}

    return {"codes": code_list}


def handle_revoke(data):
    db = db_connection()

    update_result = code_generator.update_codes(
        database=db, code=data["code"], status_details="Revoked"
    )

    return {"codes revoked": update_result}


def handle_validate(data):
    db = db_connection()
    code_to_test = data["code"]

    code_details = code_generator.get_codes(database=db, code=code_to_test)

    if len(code_details) != 1:
        return {"actor": None}

    data["active"] = True
    test_code_details = data

    try:
        valid_code_details = {
            "code": code_details[0]["code"],
            "dob": code_details[0]["dob"],
            "lpa": code_details[0]["lpa"],
            "active": code_details[0]["active"],
        }
    except KeyError:
        return {"actor": None}

    if dict(sorted(test_code_details.items())) == dict(
        sorted(valid_code_details.items())
    ):
        return {"actor": code_details[0]["actor"]}
    else:
        return {"actor": None}
