import os

from flask import Blueprint, abort, request, jsonify
from openapi_core import OpenAPI
from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator

from .errors import error_message
from .helpers import custom_logger
from . import endpoints

logger = custom_logger("code generator")

version = os.getenv("API_VERSION")
api = Blueprint("api", __name__, url_prefix=f"/{version}")

openapi = OpenAPI.from_file_path("./openapi/lpa-codes-openapi-v1.yml")
openapi_validated = FlaskOpenAPIViewDecorator(openapi)


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
@openapi_validated
def handle_healthcheck():
    response_message = "OK"

    return jsonify(response_message), 200


@api.route("/create", methods=["POST"])
@openapi_validated
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

    result, status_code = endpoints.handle_create(data=post_data)

    return jsonify(result), status_code


@api.route("/revoke", methods=["POST"])
@openapi_validated
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

    result, status_code = endpoints.handle_revoke(data=post_data)

    return jsonify(result), status_code


@api.route("/mark_used", methods=["POST"])
@openapi_validated
def mark_used_route():
    """
    Marks the given code as used (sets the expiry date)

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

    result, status_code = endpoints.handle_mark_used(data=post_data)

    return jsonify(result), status_code


@api.route("/validate", methods=["POST"])
@openapi_validated
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

    result, status_code = endpoints.handle_validate(data=post_data)
    if status_code == 500:
        return abort(500)

    return jsonify(result), status_code


@api.route("/exists", methods=["POST"])
@openapi_validated
def actor_code_exists_route():
    """
    Checks if a code exists for a given actor on an LPA

    Payload *should* be validated by API-Gateway before it gets here, but as it causes
    everything to explode if a required field is missing we are checking here also.

    Returns:
        if payload is valid - dict of matching code generated date, status code
        if payload is invalid - 400
    """
    post_data = request.get_json()

    try:
        lpa = post_data["lpa"]
        actor = post_data["actor"]
    except KeyError as e:
        logger.debug(f"Missing param from request: {e}")
        return abort(400)

    if "" in [lpa, actor]:
        logger.debug(
            f"Empty param in request: " f"{[i for i in [lpa, actor] if i == '']}"
        )
        return abort(400)

    result, status_code = endpoints.handle_exists(data=post_data)

    return jsonify(result), status_code


@api.route("/code", methods=["POST"])
@openapi_validated
def actor_code_details_route():
    """
    Returns data for an Actor Activation code

    Payload *should* be validated by API-Gateway before it gets here, but as it causes
    everything to explode if a required field is missing we are checking here also.

    Returns:
        if payload is valid - dict of matching code with active status, actor Uid,
        actor dob, code expiry date, code generated date, code last updated date,
        lpa Uid and status details.
        if payload is invalid - 400
    """
    post_data = request.get_json()

    try:
        code = post_data["code"]
    except KeyError as e:
        logger.debug(f"Missing param from request: {e}")
        return abort(400)

    if "" in [code]:
        logger.debug(f"Empty param in request: " f"{[i for i in [code] if i == '']}")
        return abort(400)

    result, status_code = endpoints.handle_code(data=post_data)

    if status_code != 200:
        abort(status_code)

    print(result)

    return jsonify(result), status_code
