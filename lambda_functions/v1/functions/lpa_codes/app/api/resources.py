from flask import Blueprint
from flask import request, jsonify

from .errors import error_message
from .helpers import custom_logger
from .endpoints import handle_create, handle_validate, handle_revoke

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

    result = handle_create(data=request.get_json())

    return jsonify(result), 200


@api.route("/revoke", methods=["POST"])
def revoke_route():
    """
    Placeholder for revoke a code endpoint
    Returns:
    json
    """

    result = handle_revoke(data=request.get_json())

    return jsonify(result), 200


@api.route("/validate", methods=["POST"])
def validate_route():
    """
    Placeholder for validate a code endpoint
    Returns:
    json
    """
    result = handle_validate(data=request.get_json())

    return jsonify(result), 200
