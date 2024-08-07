locals {
  environment       = terraform.workspace
  account           = contains(keys(var.accounts), local.environment) ? var.accounts[local.environment] : var.accounts.development
  branch_build_flag = contains(keys(var.accounts), local.environment) ? false : true
  a_record          = local.branch_build_flag ? "${local.environment}.${data.aws_route53_zone.environment_cert.name}" : data.aws_route53_zone.environment_cert.name

  default_tags = {
    business-unit          = "OPG"
    application            = "LPA-Codes"
    environment-name       = local.environment
    owner                  = "OPG Supervision"
    infrastructure-support = "OPG WebOps: opgteam@digital.justice.gov.uk"
    is-production          = local.account.is_production
    source-code            = "https://github.com/ministryofjustice/opg-data-lpa-codes"
  }

  api_name = "lpa-codes"

  api_template_vars = {
    region        = "eu-west-1"
    environment   = local.environment
    account_id    = local.account.account_id
    allowed_roles = join(", ", local.account.allowed_roles)
  }

  //Modify for new version of API
  latest_openapi_version = "v1"
  openapi_spec           = "../../lambda_functions/${local.latest_openapi_version}/openapi/${local.api_name}-openapi-${local.latest_openapi_version}.yml"
}

output "rest_arn" {
  value = aws_api_gateway_rest_api.lpa_codes.execution_arn
}
