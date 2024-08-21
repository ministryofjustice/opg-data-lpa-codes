module "lamdba_lpa_codes_v1" {
  source             = "./modules/lambda"
  environment        = local.environment
  aws_subnet_ids     = data.aws_subnet.private[*].id
  lambda_prefix      = "lpa-codes"
  logger_level       = "INFO"
  tags               = local.default_tags
  openapi_version    = "v1"
  rest_api           = aws_api_gateway_rest_api.lpa_codes
  account            = local.account
  dynamodb_table     = aws_dynamodb_table.lpa_codes
  package_type       = "Image"
  image_uri          = "${data.aws_ecr_repository.lpa_codes.repository_url}:${var.image_tag}"
  dbstream_image_uri = "${data.aws_ecr_repository.lpa_codes_dbstream.repository_url}:${var.image_tag}"
  ecr_arn            = data.aws_ecr_repository.lpa_codes.arn
}

data "aws_ecr_repository" "lpa_codes" {
  provider = aws.management
  name     = "integrations/lpa-codes-lambda"
}

data "aws_ecr_repository" "lpa_codes_dbstream" {
  provider = aws.management
  name     = "integrations/lpa-codes-dynamo-lambda"
}