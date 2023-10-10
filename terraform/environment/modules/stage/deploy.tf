resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = var.rest_api.id
  depends_on  = [var.domain_name]
  triggers = {
    redeployment = var.content_api_sha
    image_tag    = var.image_tag
  }
  lifecycle {
    create_before_destroy = true
  }
}
