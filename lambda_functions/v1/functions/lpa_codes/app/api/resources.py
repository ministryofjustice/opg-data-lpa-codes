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
    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "well hello there",
    }

    return jsonify(response)


@api.route("/create", methods=("GET", "POST"))
def handle_create():
    """
    Placeholder for create a code endpoint
    Returns:
    json
    """

    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "created",
    }

    return jsonify(response)


@api.route("/revoke", methods=("GET", "POST"))
def handle_revoke():
    """
    Placeholder for revoke a code endpoint
    Returns:
    json
    """

    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "revoked",
    }

    return jsonify(response)


@api.route("/validate", methods=("GET", "POST"))
def handle_validate():
    """
    Placeholder for validate a code endpoint
    Returns:
    json
    """

    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "valid",
    }

    return jsonify(response)