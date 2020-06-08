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
    Placeholder for create a code endpoint
    Returns:
    json
    """

    post_data = request.get_json()

    for entry in post_data["lpas"]:
        try:
            lpa = entry["lpa"]
            actor = entry["actor"]
            dob = entry["dob"]
        except KeyError:
            return abort(400)

        if "" in [lpa, actor, dob]:
            return abort(400)

    result = handle_create(data=post_data)

    return jsonify(result), 200


@api.route("/revoke", methods=["POST"])
def revoke_route():
    """
    Placeholder for revoke a code endpoint
    Returns:
    json
    """
    post_data = request.get_json()

    try:
        code = post_data["code"]
    except KeyError:
        return abort(400)

    if code == "":
        return abort(400)

    result = handle_revoke(data=post_data)

    return jsonify(result), 200


@api.route("/validate", methods=["POST"])
def validate_route():
    """
    Placeholder for validate a code endpoint
    Returns:
    json
    """
    post_data = request.get_json()
    try:
        code = post_data["code"]
        lpa = post_data["lpa"]
        dob = post_data["dob"]
    except KeyError:
        return abort(400)

    if "" in [code, lpa, dob]:
        return abort(400)

    result = handle_validate(data=post_data)

    return jsonify(result), 200
