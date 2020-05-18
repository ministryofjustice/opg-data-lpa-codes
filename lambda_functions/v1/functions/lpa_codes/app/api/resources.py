import boto3
from flask import current_app as app
from flask import Blueprint
from flask import request, jsonify

from . import code_generator
from .errors import error_message
from .helpers import custom_logger
from .lets_see_about_this import handle_create, handle_validate

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
def create_route():
    """
    Placeholder for create a code endpoint
    Returns:
    json
    """

    result = handle_create(data=request.get_json())

    return jsonify(result), 200


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
def validate_route():
    """
    Placeholder for validate a code endpoint
    Returns:
    json
    """
    result = handle_validate(data=request.get_json())

    return jsonify(result), 200
