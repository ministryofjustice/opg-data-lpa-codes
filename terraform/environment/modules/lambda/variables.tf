variable "environment" {
  description = "Name of the workspace environment"
  type        = string
}

variable "aws_subnet_ids" {
  description = "List of subnet ids to use for the lambda"
  type        = list(string)
}

variable "logger_level" {
  description = "Log level to use"
  type        = string
  default     = "INFO"
}

variable "lambda_prefix" {
  description = "The name of the lambda. Unique identifier"
  type        = string
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
  type = object({
    execution_arn = string
  })
}

variable "account" {
  description = "The account object"
  type = object({
    account_mapping    = string
    target_environment = string
  })
}

variable "dynamodb_table" {
  description = "The dynamodb table that the lambda should access"
  type = object({
    arn        = string
    stream_arn = string
  })
}

variable "image_uri" {
  description = "The image uri for main function in ECR"
  type        = string
  default     = null
}

variable "dbstream_image_uri" {
  description = "The image uri for dbstream in ECR"
  type        = string
  default     = null
}

variable "runtime" {
  description = "python runtime version"
  type        = string
  default     = null
}

variable "handler" {
  description = "handler"
  type        = string
  default     = null
}

variable "dbstream_handler" {
  description = "dbstream handler"
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