variable "environment" {
  type = string
}

variable "aws_subnet_ids" {
  type = list(string)
}

variable "logger_level" {
  type = string
}

variable "lambda_prefix" {
  type = string
}

variable "tags" {}

variable "openapi_version" {
  type = string
}

variable "rest_api" {}

variable "account" {}
