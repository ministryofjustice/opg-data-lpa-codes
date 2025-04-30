resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = var.rest_api.id

  triggers = {
    open_api_spec      = var.content_api_sha
    api_gateway_policy = var.content_api_gateway_policy_sha
    image_tag          = var.image_tag
  }

  lifecycle {
    create_before_destroy = true
  }
}
