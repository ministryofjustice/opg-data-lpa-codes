locals {
  lambda            = "${var.lambda_prefix}-${var.environment}-${var.openapi_version}"
  lambda_underscore = replace(var.lambda_prefix, "-", "_")
}

resource "aws_cloudwatch_log_group" "lambda" {
  name = "/aws/lambda/${local.lambda}"
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "lambda_dbstream" {
  name = "/aws/lambda/${local.lambda}_dbstream"
  tags = var.tags
}

resource "aws_lambda_function" "lambda_function" {
  function_name = local.lambda
  image_uri     = var.main_image_uri
  package_type  = var.package_type
  role          = aws_iam_role.lambda_role.arn
  timeout       = var.timeout
  depends_on    = [aws_cloudwatch_log_group.lambda]

  vpc_config {
    subnet_ids         = var.aws_subnet_ids
    security_group_ids = [data.aws_security_group.lambda_api_ingress.id]
  }
  environment {
    variables = {
      LOGGER_LEVEL = var.logger_level
      API_VERSION  = var.openapi_version
      ENVIRONMENT  = var.environment
    }
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

resource "aws_lambda_function" "lambda_dbstream_function" {
  function_name = "lpa-codes-dbstream-${var.environment}-${var.openapi_version}"
  role          = aws_iam_role.lambda_role.arn
  image_uri     = var.dbstream_image_uri
  package_type  = var.package_type
  timeout       = 5
  depends_on    = [aws_cloudwatch_log_group.lambda_dbstream]
  vpc_config {
    subnet_ids         = var.aws_subnet_ids
    security_group_ids = [data.aws_security_group.lambda_api_ingress.id]
  }
  environment {
    variables = {
      API_VERSION = var.openapi_version
    }
  }
  tracing_config {
    mode = "Active"
  }
  tags = var.tags
}

resource "aws_lambda_event_source_mapping" "dynamodb_stream_map" {
  event_source_arn  = var.dynamodb_table.stream_arn
  function_name     = aws_lambda_function.lambda_dbstream_function.arn
  starting_position = "LATEST"
}
