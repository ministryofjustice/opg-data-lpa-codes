module "lamdba_lpa_codes_v1" {
  source          = "./modules/lambda"
  environment     = local.environment
  aws_subnet_ids  = data.aws_subnet_ids.private.ids
  lambda_prefix   = "lpa-codes"
  logger_level    = "INFO"
  tags            = local.default_tags
  openapi_version = "v1"
  rest_api        = aws_api_gateway_rest_api.lpa_codes
  account         = local.account
}

//To Add New Version Copy and Paste Above and Modify Accordingly
