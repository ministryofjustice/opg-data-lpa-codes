def lambda_handler(event, context):
    response = {
        "isBase64Encoded": "false",
        "statusCode": "200",
        "headers": {"headerName": "headerValue"},
        "body": "everything ok",
    }
    return response
