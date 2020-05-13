from . import create_app
from .flask_lambda import FlaskLambda


http_server = create_app(FlaskLambda)
