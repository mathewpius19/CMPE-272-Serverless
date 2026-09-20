resource "aws_api_gateway_rest_api" "rest_api" {
  name = "${var.workshop_stack_base_name}_rest_api"

  body = jsonencode({
    openapi = "3.0.1"
    info    = { title = "rest_api", version = "1.0" }
    paths = {
      "/users" = {
        get = {
          x-amazon-apigateway-integration = {
            httpMethod = "POST"
            type       = "aws_proxy"
            uri        = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.userfunctions_lambda.arn}/invocations"
          }
        }
        post = {
          x-amazon-apigateway-integration = {
            httpMethod = "POST"
            type       = "aws_proxy"
            uri        = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.userfunctions_lambda.arn}/invocations"
          }
        }
      }
      "/users/{userid}" = {
        get = {
          x-amazon-apigateway-integration = {
            httpMethod = "POST"
            type       = "aws_proxy"
            uri        = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.userfunctions_lambda.arn}/invocations"
          }
        }
        put = {
          x-amazon-apigateway-integration = {
            httpMethod = "POST"
            type       = "aws_proxy"
            uri        = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.userfunctions_lambda.arn}/invocations"
          }
        }
        delete = {
          x-amazon-apigateway-integration = {
            httpMethod = "POST"
            type       = "aws_proxy"
            uri        = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.userfunctions_lambda.arn}/invocations"
          }
        }
      }
    }
  })

  endpoint_configuration { types = ["REGIONAL"] }
}

resource "aws_api_gateway_deployment" "rest_api" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.rest_api.body))
  }
  lifecycle { create_before_destroy = true }
}

resource "aws_api_gateway_stage" "rest_api" {
  deployment_id        = aws_api_gateway_deployment.rest_api.id
  rest_api_id          = aws_api_gateway_rest_api.rest_api.id
  stage_name           = "Prod"
  xray_tracing_enabled = true
}

resource "aws_lambda_permission" "allow_apigateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.userfunctions_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.rest_api.execution_arn}/*/*/*"
}

output "APIEndpoint" {
  value = aws_api_gateway_stage.rest_api.invoke_url
}
