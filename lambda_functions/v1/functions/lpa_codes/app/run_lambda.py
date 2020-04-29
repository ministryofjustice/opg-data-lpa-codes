# for python <= 3.5 update your requirements-to-freeze.txt
# to use the flask-lambda pip pacakage
from flask_lambda import FlaskLambda
from . import create_app


http_server = create_app(FlaskLambda)
