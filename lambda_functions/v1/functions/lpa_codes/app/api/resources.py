from flask import Blueprint
from flask import request, jsonify

from .errors import error_message

api = Blueprint("api", __name__)


@api.app_errorhandler(404)
def handle404(error=None):
    return error_message(404, "Not found url {}".format(request.url))


@api.app_errorhandler(405)
def handle405(error=None):
    return error_message(405, "Method not supported")


@api.app_errorhandler(500)
def handle500(error=None):
    return error_message(500, "Something went wrong")


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

    response_message = {
        "code": "example_code",
        "status": "generated",
        "id": "91d9860e-f759-4214-8ffa-bfd87a12a995",
    }

    return jsonify(response_message), 501


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
