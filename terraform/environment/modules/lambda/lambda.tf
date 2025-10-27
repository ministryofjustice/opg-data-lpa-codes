locals {
  lambda          = "${var.lambda_prefix}-${var.environment}-${var.openapi_version}"
  lambda_dbstream = "${var.lambda_prefix}-dbstream-${var.environment}-${var.openapi_version}"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name = "/aws/lambda/${local.lambda}"
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "lambda_dbstream" {
  name = "/aws/lambda/${local.lambda_dbstream}"
  tags = var.tags
}

resource "aws_lambda_function" "lambda_function" {
  function_name = local.lambda
  package_type  = "Image"
  role          = aws_iam_role.lambda_role.arn
  timeout       = var.timeout
  depends_on    = [aws_cloudwatch_log_group.lambda]

  image_uri = var.image_uri

  vpc_config {
    subnet_ids         = var.aws_subnet_ids
    security_group_ids = [data.aws_security_group.lambda_api_ingress.id]
  }

  environment {
    variables = {
      LOGGER_LEVEL = var.logger_level
      ENVIRONMENT  = var.environment
    }
  }

  logging_config {
    log_format = "JSON"
  }

  tracing_config {
    mode = "Active"
  }

  tags = var.tags
}

resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowApiLPACodesGatewayInvoke-${var.environment}-${var.openapi_version}-${var.lambda_prefix}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${var.rest_api.execution_arn}/*/*/*"
}
