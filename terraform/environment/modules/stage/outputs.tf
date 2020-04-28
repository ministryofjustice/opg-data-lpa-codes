output "stage" {
  description = "The stage"
  value       = aws_api_gateway_stage.currentstage
}

output "deployment" {
  description = "The deployment"
  value       = aws_api_gateway_deployment.deploy
}
