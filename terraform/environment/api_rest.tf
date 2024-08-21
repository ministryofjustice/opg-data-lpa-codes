resource "aws_api_gateway_rest_api" "lpa_codes" {
  name        = "lpa-codes-${local.environment}"
  description = "API Gateway for LPA Codes - ${local.environment}"
  body        = local.template_file

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    replace_triggered_by = [
      module.lamdba_lpa_codes_v1.lambda_iam_role
    ]
  }

  tags = local.default_tags
}

resource "null_resource" "open_api" {
  triggers = {
    open_api_sha = local.open_api_sha
  }
}

locals {
  template_file = templatefile(local.openapi_spec, local.api_template_vars)
  open_api_sha  = substr(replace(base64sha256(local.template_file), "/[^0-9A-Za-z_]/", ""), 0, 5)
}
