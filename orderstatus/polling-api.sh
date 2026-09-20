#!/usr/bin/env bash

set -u

if [ "$#" -lt 3 ]; then
  echo "Usage: bash polling-api.sh <api-endpoint> <order-id> <desired-status>"
  exit 2
fi

api_endpoint="$1"
order_id="$2"
desired_status="$3"

for attempt in $(seq 1 20); do
  response=$(curl -sS "$api_endpoint/orders/$order_id")
  echo "Poll $attempt: $response"

  case "$response" in
    *"\"status\": \"$desired_status\""*|*"\"status\":\"$desired_status\""*)
      echo "Order status matches desired result: $desired_status"
      exit 0
      ;;
  esac

  echo "Still waiting for $desired_status status"
  sleep 2
done

echo "Timed out waiting for $desired_status"
exit 1
