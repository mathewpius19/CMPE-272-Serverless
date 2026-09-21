import json
import os
import uuid
from datetime import datetime

import boto3

USERS_TABLE = os.getenv("USERS_TABLE")
ddb_table = boto3.resource("dynamodb").Table(USERS_TABLE)


def lambda_handler(event, context):
    route_key = f"{event['httpMethod']} {event['resource']}"
    response_body = {"Message": "Unsupported route"}
    status_code = 400
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }

    try:
        if route_key == "GET /users":
            response_body = ddb_table.scan(Select="ALL_ATTRIBUTES")["Items"]
            status_code = 200
        elif route_key == "GET /users/{userid}":
            response_body = ddb_table.get_item(
                Key={"userid": event["pathParameters"]["userid"]}
            ).get("Item", {})
            status_code = 200
        elif route_key == "DELETE /users/{userid}":
            ddb_table.delete_item(
                Key={"userid": event["pathParameters"]["userid"]}
            )
            response_body = {}
            status_code = 200
        elif route_key == "POST /users":
            request_json = json.loads(event["body"])
            request_json.setdefault("userid", str(uuid.uuid1()))
            request_json["timestamp"] = datetime.now().isoformat()
            ddb_table.put_item(Item=request_json)
            response_body = request_json
            status_code = 200
        elif route_key == "PUT /users/{userid}":
            request_json = json.loads(event["body"])
            request_json["userid"] = event["pathParameters"]["userid"]
            request_json["timestamp"] = datetime.now().isoformat()
            ddb_table.put_item(Item=request_json)
            response_body = request_json
            status_code = 200
    except Exception as error:
        response_body = {"Error": str(error)}

    return {
        "statusCode": status_code,
        "body": json.dumps(response_body),
        "headers": headers,
    }
