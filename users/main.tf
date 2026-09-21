terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.65"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.8"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.3"
    }
  }
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
