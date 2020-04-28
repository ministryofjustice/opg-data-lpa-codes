variable "environment" {
  type = string
}

variable "aws_subnet_ids" {
  type = list(string)
}

variable "vpc_id" {
  type = string
}

variable "api_name" {}

variable "tags" {}

variable "openapi_version" {}

variable "rest_api" {}

variable "domain_name" {}

variable "lpa_codes_lambda" {}
