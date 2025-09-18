locals {
  certificate_arn = local.branch_build_flag ? data.aws_acm_certificate.environment_cert[0].arn : aws_acm_certificate.environment_cert[0].arn
}

resource "aws_api_gateway_method_settings" "global_gateway_settings" {
  rest_api_id = aws_api_gateway_rest_api.lpa_codes.id
  stage_name  = module.deploy_v1.stage.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }

}

resource "aws_api_gateway_domain_name" "lpa_codes" {
  domain_name              = trimsuffix(local.a_record, ".")
  regional_certificate_arn = local.certificate_arn
  security_policy          = "TLS_1_2"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = local.default_tags
}

module "deploy_v1" {
  source = "./modules/stage"

  account_name                   = local.account.account_mapping
  lpa_codes_lambda               = module.lamdba_lpa_codes_v1.lambda
  image_tag                      = var.image_tag
  openapi_version                = "v1"
  region_name                    = data.aws_region.region.name
  rest_api                       = aws_api_gateway_rest_api.lpa_codes
  tags                           = local.default_tags
  content_api_sha                = local.open_api_sha
  content_api_gateway_policy_sha = local.rest_api_policy_sha
}

//To Add New Version Copy and Paste Above and Modify Accordingly
//Below takes the latest stage/deployment. Modify for new version.

resource "aws_api_gateway_base_path_mapping" "mapping" {
  api_id      = aws_api_gateway_rest_api.lpa_codes.id
  stage_name  = module.deploy_v1.stage.stage_name
  domain_name = aws_api_gateway_domain_name.lpa_codes.domain_name
  base_path   = module.deploy_v1.stage.stage_name
}

