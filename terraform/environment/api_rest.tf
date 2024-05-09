resource "aws_api_gateway_rest_api" "lpa_codes" {
  name        = "lpa-codes-${local.environment}"
  description = "API Gateway for LPA Codes - ${local.environment}"
  body        = local.template_file

  endpoint_configuration {
    types = ["REGIONAL"]
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

data "aws_iam_policy_document" "lpa_codes" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = local.account.allowed_roles
    }

    actions   = ["execute-api:Invoke"]
    resources = [aws_api_gateway_rest_api.lpa_codes.execution_arn]
  }
}
resource "aws_api_gateway_rest_api_policy" "lpa_codes" {
  rest_api_id = aws_api_gateway_rest_api.lpa_codes.id
  policy      = data.aws_iam_policy_document.lpa_codes.json
}
