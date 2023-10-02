from .api.resources import api as api_blueprint


def create_app(Flask):
    print("Starting Flask App")
    app = Flask(__name__)
    app.register_blueprint(api_blueprint)

    return app
