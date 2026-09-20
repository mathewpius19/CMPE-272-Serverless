import json
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.idempotency import (
    DynamoDBPersistenceLayer,
    IdempotencyConfig,
    idempotent_function,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
metrics = Metrics()
dynamodb = boto3.resource("dynamodb")
orders_table = dynamodb.Table(os.environ["TABLE_NAME"])
persistence_layer = DynamoDBPersistenceLayer(
    table_name=os.environ["IDEMPOTENCY_TABLE_NAME"]
)
idempotency_config = IdempotencyConfig(
    event_key_jmespath="powertools_json(body).orderId",
    expires_after_seconds=3600,
)


def user_id_from(event: dict) -> str:
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    headers = {key.lower(): value for key, value in (event.get("headers") or {}).items()}
    return claims.get("sub") or headers.get("x-user-id") or "demo-user"


@idempotent_function(
    data_keyword_argument="event",
    config=idempotency_config,
    persistence_store=persistence_layer,
)
def add_order(*, event: dict) -> dict:
    detail = json.loads(event.get("body") or "{}", parse_float=Decimal)
    required = {"orderId", "restaurantId", "totalAmount", "orderItems"}
    missing = sorted(required - detail.keys())
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    logger.info({"operation": "add_order", "order_details": detail})
    user_id = user_id_from(event)
    order_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    order_id = str(detail["orderId"])

    order = {
        "orderId": order_id,
        "userId": user_id,
        "restaurantId": detail["restaurantId"],
        "totalAmount": detail["totalAmount"],
        "orderItems": detail["orderItems"],
        "status": "PLACED",
        "orderTime": order_time,
    }
    orders_table.put_item(
        Item={"userId": user_id, "orderId": order_id, "data": order},
        ConditionExpression="attribute_not_exists(orderId)",
    )

    metrics.add_metric(name="SuccessfulOrder", unit=MetricUnit.Count, value=1)
    metrics.add_metric(
        name="OrderTotal", unit=MetricUnit.Count, value=float(detail["totalAmount"])
    )
    logger.info("New order saved", order_id=order_id)
    return order


@logger.inject_lambda_context
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    idempotency_config.register_lambda_context(context)
    try:
        result = add_order(event=event)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result, default=str),
        }
    except ValueError as error:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(error)}),
        }
