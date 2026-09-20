import json
import os

import boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def process_message(message: dict) -> None:
    key = {
        "userId": message["userId"],
        "restaurantId": str(message["restaurantId"]),
    }
    if message["action"] == "DELETE":
        table.delete_item(Key=key)
    else:
        favorite = {
            key: value
            for key, value in message.items()
            if key not in {"action", "userId", "restaurantId"}
        }
        table.put_item(Item={**key, "favorite": favorite})


def lambda_handler(event, context):
    failures = []
    for record in event.get("Records", []):
        try:
            process_message(json.loads(record["body"]))
        except Exception:
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}
