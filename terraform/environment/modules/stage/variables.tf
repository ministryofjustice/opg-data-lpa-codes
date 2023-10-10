variable "account_name" {
  description = "Account name to use"
  type        = string
}

variable "api_name" {
  description = "Name fo the API gateway"
  type        = string
}

variable "aws_subnet_ids" {
  description = "List of subnets"
  type        = list(string)
}

variable "domain_name" {
  description = "Domain name to use"
}

variable "lpa_codes_lambda" {
  description = "Lambda Object"
}

variable "openapi_version" {
  description = "Openapi version"
  type        = string
  default     = "v1"
}

variable "image_tag" {
  description = "Image tag for the lambda image"
  type        = string
}

variable "region_name" {
  description = "Region name"
  type        = string
}

variable "rest_api" {
  description = "The rest API Object"
}

variable "tags" {
  description = "Tags to use"
}

variable "content_api_sha" {
  description = "SHA for the content of the openapi spec"
  type        = string
}
