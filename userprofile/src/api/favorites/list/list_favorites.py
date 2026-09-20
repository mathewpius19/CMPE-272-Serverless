import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def user_id_from(event: dict) -> str:
    headers = {key.lower(): value for key, value in (event.get("headers") or {}).items()}
    return headers.get("x-user-id") or "demo-user"


def encode(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError


def lambda_handler(event, context):
    result = table.query(KeyConditionExpression=Key("userId").eq(user_id_from(event)))
    favorites = [
        {
            "restaurantId": item["restaurantId"],
            **item.get("favorite", {}),
        }
        for item in result.get("Items", [])
    ]
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"favorites": favorites}, default=encode),
    }
