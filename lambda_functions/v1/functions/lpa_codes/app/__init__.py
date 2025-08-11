from flask_openapi3 import Info, Server
from .api.resources import api as api_blueprint
from .responses import gateway_responses, validation_error_callback, Error400

api_key = {
    "type": "apiKey",
    "name": "Authorization",
    "in": "header",
    "x-amazon-apigateway-authtype": "awsSigv4",
    "x-apikeyInfoFunc": "lpa_codes_mock.apikey_auth",  # pragma: allowlist secret
}
security_schemes = {
    "sigv4": api_key,
}

extensions = {
    "x-amazon-apigateway-request-validators": {
        "all": {"validateRequestParameters": True, "validateRequestBody": True}
    },
    "x-amazon-apigateway-gateway-responses": gateway_responses,
}


def create_app(OpenAPI):
    print("Starting Flask App")

    info = Info(title="lpa-codes-${environment}", version="1.0")
    servers = [
        Server(
            url="/v1",
            description="Specify prefix only so service can be used in different "
            "environments.",
        ),
    ]

    app = OpenAPI(
        __name__,
        info=info,
        servers=servers,
        security_schemes=security_schemes,
        openapi_extensions=extensions,
        validation_error_status=400,
        validation_error_model=Error400,
        validation_error_callback=validation_error_callback,
    )
    app.register_api(api_blueprint)

    return app
