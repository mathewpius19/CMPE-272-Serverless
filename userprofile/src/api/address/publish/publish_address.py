import json
import os
import uuid

import boto3

eventbridge = boto3.client("events")
event_bus_name = os.environ["EVENT_BUS_NAME"]


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
        detail_type = "address.added"
        detail.setdefault("addressId", str(uuid.uuid4()))
    elif method == "PUT":
        detail_type = "address.updated"
        detail["addressId"] = event["pathParameters"]["addressId"]
    elif method == "DELETE":
        detail_type = "address.deleted"
        detail = {
            "userId": detail["userId"],
            "addressId": event["pathParameters"]["addressId"],
        }
    else:
        return response(405, {"error": "Method not allowed"})

    result = eventbridge.put_events(
        Entries=[
            {
                "Source": "customer-profile",
                "DetailType": detail_type,
                "Detail": json.dumps(detail),
                "EventBusName": event_bus_name,
            }
        ]
    )
    if result.get("FailedEntryCount", 0):
        return response(500, {"error": "EventBridge rejected the event"})

    return response(
        202,
        {
            "status": "ACCEPTED",
            "pattern": "EventBridge asynchronous invocation",
            "eventId": result["Entries"][0]["EventId"],
            "detailType": detail_type,
            "addressId": detail["addressId"],
        },
    )
