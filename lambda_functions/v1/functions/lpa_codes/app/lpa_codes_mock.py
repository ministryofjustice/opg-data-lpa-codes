import connexion
import boto3
import os
from botocore.exceptions import ClientError
from flask import request, jsonify
from connexion.exceptions import OAuthProblem

TOKEN_DB = {"asdf1234567890": {"uid": 100}}


def apikey_auth(token, required_scopes):
    info = TOKEN_DB.get(token, None)

    if not info:
        raise OAuthProblem("Invalid token")

    return info


def dynamodb_connection(conn="resource"):
    if os.environ.get("LOCAL_URL") is not None:
        local_url = os.environ.get("LOCAL_URL")
    else:
        local_url = "localhost"
    if conn == "resource":
        ddb = boto3.resource(
            "dynamodb",
            endpoint_url="http://" + local_url + ":8000",
            region_name="eu-west-1",
        )
    else:
        ddb = boto3.client(
            "dynamodb",
            endpoint_url="http://" + local_url + ":8000",
            region_name="eu-west-1",
        )
    return ddb


def create_table_default():
    ddb = dynamodb_connection(conn="client")
    try:
        ddb.create_table(
            TableName="lpa-codes-local",
            KeySchema=[{"AttributeName": "code", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "code", "AttributeType": "S"},
                {"AttributeName": "lpa", "AttributeType": "S"},
                {"AttributeName": "actor", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "key_index",
                    "KeySchema": [
                        {"AttributeName": "lpa", "KeyType": "HASH"},
                        {"AttributeName": "actor", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5,
                    },
                }
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
        )
        return "Table created"
    except ddb.exceptions.ResourceInUseException:
        return "Table already exists: " + str(
            ddb.describe_table(TableName="lpa-codes-local")
        )


def create_table(table_name, body):
    ddb = dynamodb_connection(conn="client")
    try:
        table = ddb.create_table(
            TableName=table_name,
            KeySchema=body["KeySchema"],  # Partition key
            AttributeDefinitions=body["AttributeDefinitions"],
            ProvisionedThroughput=body["ProvisionedThroughput"],
        )
        for index in body["Indexes"]:
            table.update(GlobalSecondaryIndexUpdates=index)
        return "Table created"
    except ddb.exceptions.ResourceInUseException:
        return "Table already exists"


def list_tables():
    ddb = dynamodb_connection(conn="client")
    return ddb.list_tables()


def delete_table(table_name):
    ddb = dynamodb_connection(conn="client")
    params = {"TableName": table_name}
    try:
        ddb.delete_table(**params)
        print("Waiting for", table_name, "...")
        waiter = ddb.get_waiter("table_not_exists")
        waiter.wait(TableName=table_name)
        return "table deleted"
    except ddb.exceptions.ResourceNotFoundException:
        return "table doesn't exist"


def clear_all():
    ddb = dynamodb_connection(conn="client")
    for table in ddb.list_tables()["TableNames"]:
        delete_table(table)
    print("Tables to be destroyed: " + str(ddb.list_tables()))
    return "All tables destroyed"


def create_rows(table_name, body):
    table = dynamodb_connection(conn="resource").Table(table_name)
    count = 0
    for data in body["rows"]:
        try:
            table.put_item(Item=data)
            count = count + 1
        except ClientError as e:
            print(e.response["Error"]["Message"])
    return str(count) + " rows created!"


def delete_rows(table_name, body):
    table = dynamodb_connection(conn="resource").Table(table_name)
    count = 0
    for row in body["rows"]:
        try:
            response = table.delete_item(Key=row)
            count = count + 1
        except ClientError as e:
            print(e.response["Error"]["Message"])
    return str(count) + " rows deleted! " + str(response)


def get_rows(table_name, body):
    table = dynamodb_connection(conn="resource").Table(table_name)
    response = table.get_item(Key=body)
    if "Item" in response:
        return response["Item"]
    else:
        return "No row found!"


def get_all_rows(table_name):
    table = dynamodb_connection(conn="resource").Table(table_name)
    all_rows = []
    response = table.scan()
    for row in response["Items"]:
        all_rows.append(row)
    return all_rows


# PACT Specific functions
def update_state():
    mapping = {
        "generated code exists and active": setup_code_active,
        "generated code exists and not active": setup_code_not_active,
    }
    mapping[request.json["state"]]()
    return jsonify({"result": request.json["state"]})


def setup_code_active():
    table = dynamodb_connection(conn="resource").Table("lpa_codes")

    data = {
        "active": True,
        "actor": "humphrey",
        "code": "yEFJH33hn5nX",
        "expiry_date": "10/11/2020",
        "generated_date": "11/11/2019",
        "last_updated_date": "19/06/2020",
        "lpa": "streamline_distributed_content",
    }
    table.put_item(Item=data)
    return "Data SetUp"


def setup_code_not_active():
    table = dynamodb_connection(conn="resource").Table("lpa_codes")

    data = {
        "active": False,
        "actor": "humphrey",
        "code": "yEFJH33hn5nX",
        "expiry_date": "10/11/2020",
        "generated_date": "11/11/2019",
        "last_updated_date": "19/06/2020",
        "lpa": "streamline_distributed_content",
    }
    table.put_item(Item=data)
    return table


mock = connexion.FlaskApp(__name__, specification_dir="../../../openapi/")
mock.add_api("lpa-codes-openapi-v1.yml")
mock.add_api("state-openapi-v1.yml")
mock.run(port=4343)
