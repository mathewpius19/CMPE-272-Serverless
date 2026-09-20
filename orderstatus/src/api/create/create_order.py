import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3

table = boto3.resource("dynamodb").Table(os.environ["ORDERS_TABLE_NAME"])


def encode(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError


def lambda_handler(event, context):
    detail = json.loads(event.get("body") or "{}", parse_float=Decimal)
    order_id = str(detail.get("orderId") or uuid.uuid4())
    order = {
        "orderId": order_id,
        "status": "PLACED",
        "restaurantId": detail.get("restaurantId", 1),
        "orderItems": detail.get("orderItems", []),
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    table.put_item(
        Item=order,
        ConditionExpression="attribute_not_exists(orderId)",
    )
    return {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(order, default=encode),
    }
