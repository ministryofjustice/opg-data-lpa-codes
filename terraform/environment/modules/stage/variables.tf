variable "account_name" {
  description = "Account name to use"
  type        = string
}

variable "lpa_codes_lambda" {
  description = "Lambda Object"
  type = object({
    function_name = string
  })
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
  type = object({
    id   = string
    name = string
  })
}

variable "tags" {
  description = "Tags to use"
  type        = map(string)
  default     = {}
}

variable "content_api_sha" {
  description = "SHA for the content of the openapi spec"
  type        = string
}
