variable "default_role" {
  default = "sirius-ci"
}

variable "management_role" {
  default = "sirius-ci"
}

variable "accounts" {
  type = map(
    object({
      account_id         = string
      account_mapping    = string
      is_production      = string
      vpc_id             = string
      opg_hosted_zone    = string
      allowed_roles      = list(string)
      target_environment = string
      threshold          = number
    })
  )
}
