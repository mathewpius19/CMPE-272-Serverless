import json
import os

import boto3

sqs = boto3.client("sqs")
queue_url = os.environ["QUEUE_URL"]


def user_id_from(event: dict) -> str:
    headers = {key.lower(): value for key, value in (event.get("headers") or {}).items()}
    return headers.get("x-user-id") or "demo-user"


def response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    method = event["httpMethod"]
    detail = json.loads(event.get("body") or "{}")
    detail["userId"] = user_id_from(event)

    if method == "POST":
        if "restaurantId" not in detail:
            return response(400, {"error": "restaurantId is required"})
        action = "ADD"
    elif method == "DELETE":
        action = "DELETE"
        detail = {
            "userId": detail["userId"],
            "restaurantId": event["pathParameters"]["restaurantId"],
        }
    else:
        return response(405, {"error": "Method not allowed"})

    message = {"action": action, **detail}
    result = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
    return response(
        202,
        {
            "status": "ACCEPTED",
            "pattern": "SQS asynchronous invocation",
            "messageId": result["MessageId"],
            "restaurantId": str(detail["restaurantId"]),
        },
    )
