# Module 3 - Synchronous Invocation with Idempotence

This self-contained AWS SAM application deploys an Orders REST API, an Orders
DynamoDB table, and an idempotency DynamoDB table. Repeating the same `POST
/orders` request with the same `orderId` returns the cached result instead of
creating another order.

## Deploy

```bash
sam build
sam deploy
```

## Demonstrate idempotence

```bash
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ws-serverless-patterns-orders \
  --query "Stacks[0].Outputs[?OutputKey=='OrdersServiceEndpoint'].OutputValue" \
  --output text)

ORDER_ID="module3-$(date +%s)"
BODY=$(printf '{"orderId":"%s","restaurantId":1,"totalAmount":19.97,"orderItems":[{"id":1,"name":"Pizza","price":19.97,"quantity":1}]}' "$ORDER_ID")

curl -s -X POST "$API_ENDPOINT/orders" -H 'Content-Type: application/json' -H 'X-User-Id: demo-user' -d "$BODY"
curl -s -X POST "$API_ENDPOINT/orders" -H 'Content-Type: application/json' -H 'X-User-Id: demo-user' -d "$BODY"
curl -s "$API_ENDPOINT/orders" -H 'X-User-Id: demo-user'
```

The two POST responses should contain the same `orderId`, and the final list
should contain only one copy of that order.

## Cleanup

```bash
sam delete --stack-name ws-serverless-patterns-orders --no-prompts
```
