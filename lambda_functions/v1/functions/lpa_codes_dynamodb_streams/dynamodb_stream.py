from __future__ import print_function


def lambda_handler(event, context):
    for record in event["Records"]:
        print(record["eventName"])
        print(record["dynamodb"])
