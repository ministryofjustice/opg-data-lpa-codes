from flask import Blueprint
from flask import request, jsonify

from . import code_generator
from .errors import error_message
from .helpers import custom_logger


logger = custom_logger("code generator")


api = Blueprint("api", __name__)


@api.app_errorhandler(404)
def handle404(error=None):
    return error_message(404, "Not found url {}".format(request.url))


@api.app_errorhandler(405)
def handle405(error=None):
    return error_message(405, "Method not supported")


@api.app_errorhandler(500)
def handle500(error=None):
    return error_message(500, f"Something went wrong: {error}")


@api.route("/healthcheck", methods=("HEAD", "GET"))
def handle_healthcheck():
    response_message = "OK"

    return jsonify(response_message), 200


@api.route("/create", methods=("GET", "POST"))
def handle_create():
    """
    Placeholder for create a code endpoint
    Returns:
    json
    """
    logger.info("starting create endpoint")

    data = request.get_json()

    logger.info(f"data: {data}")

    code_list = []

    for entry in data:
        key = {"lpa": entry["lpa"], "actor": entry["actor"]}
        logger.info(f"key: {key}")

        # 1. expire all existing codes for LPA/Actor combo
        code_generator.update_codes(key=key, status=False)

        # 2. generate a new code
        generated_code = code_generator.generate_code()

        # 3. insert new code into database
        new_code = code_generator.insert_new_code(key=key, code=generated_code)

        logger.info(f"new code is this: {new_code}")
        # new_code = {}
        # new_code['code'] = 'this is code'

        # 4. return the new code in lambda payload
        response = {
            "lpa": entry["lpa"],
            "actor": entry["actor"],
            "code": new_code[0]["code"],
        }

        code_list.append(response)

    return jsonify(code_list), 200


@api.route("/revoke", methods=("GET", "POST"))
def handle_revoke():
    """
    Placeholder for revoke a code endpoint
    Returns:
    json
    """

    response_message = {
        "code": "example_code",
        "status": "revoked",
        "id": "33857363-76cb-4d7e-9f1f-740e04a5456d",
    }

    return jsonify(response_message), 501


@api.route("/validate", methods=("GET", "POST"))
def handle_validate():
    """
    Placeholder for validate a code endpoint
    Returns:
    json
    """

    response_message = {
        "code": "example_code",
        "status": "valid",
        "id": "7c94fd39-7680-43a8-ba25-7430760c52b3",
    }

    return jsonify(response_message), 501
