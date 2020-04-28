data "template_file" "_" {
  template = local.openapispec
  vars     = local.api_template_vars
}

// Bug - Recreates api gateway spec on each build!
// Can't use Lifecycle ignore changes as not attaching policy on first build!
// https://github.com/terraform-providers/terraform-provider-aws/issues/5549
resource "aws_api_gateway_rest_api" "lpa_codes" {
  name        = "lpa-codes-${local.environment}"
  description = "API Gateway for LPA Codes - ${local.environment}"
  policy      = data.aws_iam_policy_document.resource_policy.json
  body        = data.template_file._.rendered

  endpoint_configuration {
    types = ["REGIONAL"]
  }
  tags = local.default_tags
}
