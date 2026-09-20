#!/usr/bin/env bash

set -eu

if [ "$#" -lt 3 ]; then
  echo "Usage: bash publish-update.sh <event-bus-name> <order-id> <status>"
  exit 2
fi

event_bus_name="$1"
order_id="$2"
new_status="$3"

entries=$(python3 -c 'import json,sys; print(json.dumps([{"EventBusName":sys.argv[1],"Source":"restaurant","DetailType":"order.updated","Detail":json.dumps({"data":{"orderId":sys.argv[2],"status":sys.argv[3]}})}]))' "$event_bus_name" "$order_id" "$new_status")

aws events put-events --region us-east-1 --entries "$entries"
