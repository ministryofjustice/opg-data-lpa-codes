import datetime

import boto3


def update_existing_codes(keys, status=False):

    table = boto3.resource("dynamodb").Table("lpa_codes")

    set_active_flag = f"active = {status}"
    set_status_updates = (
        f"last_updated_date = " f"{datetime.datetime.now().strftime('%d/%m/%Y')}"
    )

    for key in keys:
        table.update_item(
            Key={"lpa": key["lpa"], "actor": key["actor"], "code": key["code"]},
            UpdateExpression=f"SET {set_active_flag}, {set_status_updates}",
        )

    return "updated"
