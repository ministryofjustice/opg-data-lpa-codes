import json


def lambda_handler(event, context):
    for record in event["Records"]:
        recordtoprint = {}
        record["dynamodb"]["NewImage"]["code"] = hash(
            str(record["dynamodb"]["NewImage"]["code"])
        )
        recordtoprint["EventName"] = record["eventName"]
        recordtoprint["NewImage"] = record["dynamodb"]["NewImage"]

        if "OldImage" in record["dynamodb"]:
            record["dynamodb"]["OldImage"]["code"] = hash(
                str(record["dynamodb"]["OldImage"]["code"])
            )
            recordtoprint["OldImage"] = record["dynamodb"]["OldImage"]

        print(json.dumps(recordtoprint))
