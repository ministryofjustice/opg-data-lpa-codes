data "template_file" "_" {
  template = local.openapi_spec
  vars     = local.api_template_vars
}

resource "aws_api_gateway_rest_api" "lpa_codes" {
  name        = "lpa-codes-${local.environment}"
  description = "API Gateway for LPA Codes - ${local.environment}"
  body        = data.template_file._.rendered

  endpoint_configuration {
    types = ["REGIONAL"]
  }
  tags = local.default_tags
}
