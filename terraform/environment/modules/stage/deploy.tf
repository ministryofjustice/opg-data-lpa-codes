resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = var.rest_api.id

  triggers = {
    redeployment = var.content_api_sha
    image_tag    = var.image_tag
  }

  lifecycle {
    create_before_destroy = true
  }
}
