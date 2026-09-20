import json
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def user_id_from(event: dict) -> str:
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    headers = {key.lower(): value for key, value in (event.get("headers") or {}).items()}
    return claims.get("sub") or headers.get("x-user-id") or "demo-user"


def encode(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError


def lambda_handler(event, context):
    user_id = user_id_from(event)
    order_id = event["pathParameters"]["orderId"]
    result = table.get_item(Key={"userId": user_id, "orderId": order_id})
    item = result.get("Item")
    if not item:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Order not found"}),
        }

    order = item["data"]
    order["status"] = "CANCELLED"
    order["cancelTime"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    table.put_item(Item={"userId": user_id, "orderId": order_id, "data": order})
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(order, default=encode),
    }
