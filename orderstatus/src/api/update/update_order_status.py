import os
from datetime import datetime, timezone

import boto3

table = boto3.resource("dynamodb").Table(os.environ["ORDERS_TABLE_NAME"])


def lambda_handler(event, context):
    order_data = event["detail"]["data"]
    order_id = str(order_data["orderId"])
    status = str(order_data["status"])
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    table.update_item(
        Key={"orderId": order_id},
        UpdateExpression="SET #order_status = :status, updatedAt = :updated_at",
        ExpressionAttributeNames={"#order_status": "status"},
        ExpressionAttributeValues={
            ":status": status,
            ":updated_at": updated_at,
        },
        ConditionExpression="attribute_exists(orderId)",
    )
    return {
        "processed": True,
        "orderId": order_id,
        "status": status,
        "updatedAt": updated_at,
    }
