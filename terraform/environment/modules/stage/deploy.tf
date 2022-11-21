resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = var.rest_api.id
  depends_on  = [var.domain_name]
  triggers = {
    redeployment              = var.content_api_sha
    lambda_version_folder_sha = var.lpa_codes_lambda.source_code_hash
  }
  lifecycle {
    create_before_destroy = true
  }
}
