data "aws_security_group" "lambda_api_ingress" {
  filter {
    name   = "tag:Name"
    values = ["integration-lambda-api-access-${local.account.target_environment}"]
  }
}
