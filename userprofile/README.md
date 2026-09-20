# Module 4 - Asynchronous Invocation

This self-contained SAM application demonstrates both asynchronous patterns
from Module 4:

- Address commands are published to a custom EventBridge bus and processed by
  a consumer Lambda function.
- Favorite restaurant commands are placed on an SQS queue and processed by a
  Lambda event-source mapping.

Both command endpoints return HTTP 202 before DynamoDB processing completes.

## Deploy

```bash
sam build
sam deploy
```

## Cleanup

```bash
sam delete --stack-name ws-serverless-patterns-userprofile --no-prompts
```
