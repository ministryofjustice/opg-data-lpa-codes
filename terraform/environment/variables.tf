variable "default_role" {
  default     = "integrations-ci"
  description = "The default role to use for the deployment"
  type        = string
}

variable "management_role" {
  default     = "integrations-ci"
  description = "The role to use for the management account"
  type        = string
}

variable "image_tag" {
  default     = "latest"
  description = "image tag to use for the deployment"
  type        = string
}

variable "accounts" {
  description = "The accounts to deploy to"
  type = map(
    object({
      account_id         = string
      account_mapping    = string
      backups_enabled    = string
      is_production      = string
      vpc_id             = string
      opg_hosted_zone    = string
      allowed_roles      = list(string)
      target_environment = string
      pit_recovery_flag  = bool
    })
  )
}
