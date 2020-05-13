import boto3

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator
from lambda_functions.v1.functions.lpa_codes.app.api.helpers import (
    custom_logger,
    db_client,
)

logger = custom_logger("code generator")


def handle_create(data):
    """
    Placeholder for create a code endpoint
    Returns:
    json
    """

    db_resource = boto3.resource("dynamodb")

    code_list = []

    for entry in data["lpas"]:

        key = {"lpa": entry["lpa"], "actor": entry["actor"]}

        # 1. expire all existing codes for LPA/Actor combo
        # code_generator.update_codes(database=database, key=key, status=False)

        # 2. generate a new code
        generated_code = code_generator.generate_code(database=db_resource)

        # 3. insert new code into database
        new_code = code_generator.insert_new_code(
            database=db_resource, key=key, code=generated_code
        )[0]["code"]

        # 4. return the new code in lambda payload
        response = {
            "lpa": entry["lpa"],
            "actor": entry["actor"],
            "code": new_code,
        }

        code_list.append(response)

    return code_list
