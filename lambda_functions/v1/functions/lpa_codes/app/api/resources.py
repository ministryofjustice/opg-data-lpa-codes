import json
import os

from flask import Blueprint, abort
from flask import request, jsonify

from .errors import error_message
from .helpers import custom_logger
from .endpoints import handle_create, handle_validate, handle_revoke

logger = custom_logger("code generator")

version = os.getenv("API_VERSION")
api = Blueprint("api", __name__, url_prefix=f"/{version}")


@api.app_errorhandler(404)
def handle404(error=None):
    return error_message(404, "Not found url {}".format(request.url))


@api.app_errorhandler(405)
def handle405(error=None):
    return error_message(405, "Method not supported")


@api.app_errorhandler(400)
def handle400(error=None):
    return error_message(400, "Bad payload")


@api.app_errorhandler(500)
def handle500(error=None):
    return error_message(500, f"Something went wrong: {error}")


@api.route("/healthcheck", methods=["HEAD", "GET"])
def handle_healthcheck():
    response_message = "OK"

    return jsonify(response_message), 200


@api.route("/create", methods=["POST"])
def create_route():
    """
    Creates a new code for the given lpa/actor/dob combo.

    Payload *should* be validated by API-Gateway before it gets here, but as it causes
    everything to explode if a required field is missing we are checking here also.

    Returns:
        tuple: (json result of handle_create method, status code)
    """

    post_data = request.get_json()

    for entry in post_data["lpas"]:
        try:
            lpa = entry["lpa"]
            actor = entry["actor"]
            dob = entry["dob"]
        except KeyError as e:
            logger.debug(f"Missing param from request: {e}")
            return abort(400)

        if "" in [lpa, actor, dob]:
            logger.debug(
                f"Empty param in request: "
                f"{[i for i in [lpa, actor, dob] if i == '']}"
            )
            return abort(400)

    result, status_code = handle_create(data=post_data)

    return jsonify(result), status_code


@api.route("/revoke", methods=["POST"])
def revoke_route():
    """
    Revokes the given code

    Payload *should* be validated by API-Gateway before it gets here, but as it causes
    everything to explode if a required field is missing we are checking here also.

    Returns:
        if payload is valid - dict of the posted data, status code
        if payload is invalid - 400
    """
    post_data = request.get_json()

    try:
        code = post_data["code"]
    except KeyError as e:
        logger.debug(f"Missing param from request: {e}")
        return abort(400)

    if code == "":
        logger.debug(f"Empty param in request: code")
        return abort(400)

    result, status_code = handle_revoke(data=post_data)

    return jsonify(result), status_code


@api.route("/validate", methods=["POST"])
def validate_route():
    """
    Validates a code/lpa/dob combo

    Payload *should* be validated by API-Gateway before it gets here, but as it causes
    everything to explode if a required field is missing we are checking here also.

    Returns:
        if payload is valid - dict of the posted data, status code
        if payload is invalid - 400
    """
    post_data = request.get_json()
    try:
        code = post_data["code"]
        lpa = post_data["lpa"]
        dob = post_data["dob"]
    except KeyError as e:
        logger.debug(f"Missing param from request: {e}")
        return abort(400)

    if "" in [code, lpa, dob]:
        logger.debug(
            f"Empty param in request: " f"{[i for i in [lpa, code, dob] if i == '']}"
        )
        return abort(400)

    result, status_code = handle_validate(data=post_data)

    return jsonify(result), status_code
