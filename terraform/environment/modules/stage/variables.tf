variable "account_name" {}

variable "api_name" {}

variable "aws_subnet_ids" {
  type = list(string)
}

variable "domain_name" {}

variable "environment" {
  type = string
}

variable "lpa_codes_lambda" {}

variable "openapi_version" {
  type    = string
  default = "v1"
}

variable "region_name" {}

variable "rest_api" {}

variable "tags" {}

variable "vpc_id" {
  type = string
}

variable "content_api_sha" {
  type = string
}
