import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

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
    response = table.query(KeyConditionExpression=Key("userId").eq(user_id_from(event)))
    orders = [item["data"] for item in response.get("Items", [])]
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"orders": orders}, default=encode),
    }
