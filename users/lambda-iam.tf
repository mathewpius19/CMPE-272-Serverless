resource "null_resource" "build_dependencies" {
  provisioner "local-exec" {
    command = "python3 -m pip install -r src/users/requirements.txt -t src/users/python"
  }

  triggers = {
    dependencies = filemd5("src/users/requirements.txt")
    source       = filemd5("src/users/lambda_function.py")
  }
}

resource "aws_iam_role" "userfunctions_lambda_role" {
  name        = "${var.workshop_stack_base_name}_userfunctions_lambda_role"
  description = "Lambda function IAM role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Action": "sts:AssumeRole",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Effect": "Allow"
  }]
}
EOF
}

resource "aws_iam_policy" "userfunctions_lambda_role_policy" {
  name        = "${var.workshop_stack_base_name}_userfunctions_lambda_role_policy"
  description = "Lambda function policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["dynamodb:GetItem", "dynamodb:DeleteItem", "dynamodb:PutItem", "dynamodb:Scan", "dynamodb:Query", "dynamodb:UpdateItem", "dynamodb:BatchWriteItem", "dynamodb:BatchGetItem", "dynamodb:DescribeTable", "dynamodb:ConditionCheckItem"]
        Resource = aws_dynamodb_table.users_table.arn
      },
      {
        Effect   = "Allow"
        Action   = ["logs:*"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["xray:*"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "userfunctions_lambda_attach" {
  role       = aws_iam_role.userfunctions_lambda_role.name
  policy_arn = aws_iam_policy.userfunctions_lambda_role_policy.arn
}

resource "aws_lambda_function" "userfunctions_lambda" {
  filename         = data.archive_file.userfunctions_lambda_zip.output_path
  function_name    = "${var.workshop_stack_base_name}_userfunctions_lambda"
  description      = "Handler for all users related operations"
  role             = aws_iam_role.userfunctions_lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.userfunctions_lambda_zip.output_base64sha256
  runtime          = var.lambda_runtime
  memory_size      = var.lambda_memory
  timeout          = var.lambda_timeout

  tracing_config { mode = var.lambda_tracing_config }

  environment {
    variables = { USERS_TABLE = aws_dynamodb_table.users_table.id }
  }
}

output "userfunctions_lambda" {
  value = aws_lambda_function.userfunctions_lambda.function_name
}
