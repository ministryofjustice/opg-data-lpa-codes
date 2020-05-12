import connexion


mock = connexion.FlaskApp(__name__, specification_dir="openapi/")
mock.add_api("lpa-codes-openapi-v1.yml")
mock.run(port=4343)
