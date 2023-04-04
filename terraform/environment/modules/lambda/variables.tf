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

variable "tags" {
  description = "A map of tags to use."
  type        = map(string)
  default     = {}
}

variable "openapi_version" {
  description = "openapi version to use"
  type        = string
}

variable "rest_api" {
  description = "The rest api lambda attached to"
}

variable "account" {
  description = "The account object"
}

variable "dynamodb_table" {
  description = "The dynamodb table that the lambda should access"
}

variable "main_image_uri" {
  description = "The image uri for main function in ECR"
  type        = string
  default     = null
}

variable "dbstream_image_uri" {
  description = "The image uri for dbstream in ECR"
  type        = string
  default     = null
}

variable "ecr_arn" {
  description = "The ECR arn for lambda image"
  type        = string
  default     = null
}

variable "package_type" {
  description = "The Lambda deployment package type"
  type        = string
  default     = "Image"
}

variable "timeout" {
  description = "The amount of time your Lambda Function has to run in seconds"
  type        = number
  default     = 30
}
