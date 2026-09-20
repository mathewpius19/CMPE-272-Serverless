import os

import boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    detail_type = event["detail-type"]
    detail = event["detail"]
    key = {"userId": detail["userId"], "addressId": detail["addressId"]}

    if detail_type == "address.deleted":
        table.delete_item(Key=key)
    else:
        table.put_item(Item={**key, "address": detail})

    return {"processed": True, "detailType": detail_type, **key}
