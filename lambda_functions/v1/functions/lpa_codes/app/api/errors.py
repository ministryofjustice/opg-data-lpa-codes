from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_message(code, message):
    """
    error_message wraps an error into payload format expected by the API client
    """

    return (
        jsonify(
            {
                "isBase64Encoded": False,
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "error": {
                        "code": HTTP_STATUS_CODES.get(code, code),
                        "message": message,
                    }
                },
            }
        ),
        code,
    )


# def unprocessable_entity(errors):
#
#     pair = list(errors.items())[0]
#     print(f"pair: {pair}")
#     message = "Key {}. {}".format(pair[0], " ".join(pair[1]))
#     print(f"message: {message}")
#     return error_message(422, message)
