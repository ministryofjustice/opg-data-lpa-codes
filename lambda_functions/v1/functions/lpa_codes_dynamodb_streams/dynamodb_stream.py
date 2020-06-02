from __future__ import print_function


def lambda_handler(event, context):
    for record in event["Records"]:
        record_to_print = {}
        record["dynamodb"]["NewImage"]["code"] = hash(
            str(record["dynamodb"]["NewImage"]["code"])
        )
        record_to_print["EventName"] = record["eventName"]
        record_to_print["NewImage"] = record["dynamodb"]["NewImage"]

        if "OldImage" in record["dynamodb"]:
            record["dynamodb"]["OldImage"]["code"] = hash(
                str(record["dynamodb"]["OldImage"]["code"])
            )
            record_to_print["OldImage"] = record["dynamodb"]["OldImage"]

        print(str(record_to_print))
