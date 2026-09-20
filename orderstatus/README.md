# Module 5 - Polling for long-running task status

This standalone SAM application demonstrates the Module 5 polling pattern:

1. A client creates an order and receives its initial `PLACED` status.
2. The client polls `GET /orders/{orderId}` without holding open the original
   create request.
3. A restaurant publishes an `order.updated` event to EventBridge.
4. A Lambda consumer updates the order in DynamoDB.
5. The next poll observes `IN-PROCESS` and finishes.

## Deploy

```bash
sam build
sam deploy
```

## Cleanup

```bash
sam delete --stack-name ws-serverless-patterns-polling --no-prompts
```
