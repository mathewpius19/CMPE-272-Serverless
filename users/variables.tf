variable "region" { default = "us-east-1" }
variable "workshop_stack_base_name" {
  default = "ws-serverless-patterns"
}

variable "lambda_memory" { default = 128 }
variable "lambda_runtime" { default = "python3.12" }
variable "lambda_timeout" { default = 100 }
variable "lambda_tracing_config" { default = "Active" }
