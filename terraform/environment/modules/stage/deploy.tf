data "local_file" "openapispec" {
  filename = "../../docs/openapi/${var.api_name}-openapi-${var.openapi_version}.yml"
}

data "local_file" "lambda_version_folder_sha" {
  filename = "../../lambda_functions/${var.openapi_version}/directory_sha"
}

resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = var.rest_api.id
  depends_on  = [var.domain_name]
  variables = {
    // Force a deploy on when content has changed
    stage_version             = var.openapi_version
    content_api_sha           = substr(replace(base64sha256(data.local_file.openapispec.content_base64), "/[^0-9A-Za-z_]/", ""), 0, 5)
    lambda_version_folder_sha = substr(replace(base64sha256(data.local_file.lambda_version_folder_sha.content_base64), "/[^0-9A-Za-z_]/", ""), 0, 5)
  }
  lifecycle {
    create_before_destroy = true
  }
}
