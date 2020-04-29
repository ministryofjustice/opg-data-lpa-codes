locals {
  lambda            = "${var.lambda_prefix}-${var.environment}-${var.openapi_version}"
  lambda_underscore = replace(var.lambda_prefix, "-", "_")
}

resource "aws_cloudwatch_log_group" "lambda" {
  name = "/aws/lambda/${local.lambda}"
  tags = var.tags
}

resource "aws_lambda_function" "lambda_function" {
  filename         = data.archive_file.lambda_archive.output_path
  source_code_hash = data.archive_file.lambda_archive.output_base64sha256
  function_name    = local.lambda
  role             = aws_iam_role.lambda_role.arn
  //  handler          = "app.${var.lambda_prefix}.lambda_handler"
  handler    = "app.run_lambda.http_server"
  runtime    = "python3.7"
  timeout    = 5
  depends_on = [aws_cloudwatch_log_group.lambda]
  layers     = [aws_lambda_layer_version.lambda_layer.arn]
  vpc_config {
    subnet_ids         = var.aws_subnet_ids
    security_group_ids = [data.aws_security_group.lambda_api_ingress.id]
  }
  environment {
    variables = {
      LOGGER_LEVEL = var.logger_level
      API_VERSION  = var.openapi_version
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

resource "aws_lambda_layer_version" "lambda_layer" {
  filename         = data.archive_file.lambda_layer_archive.output_path
  source_code_hash = data.archive_file.lambda_layer_archive.output_base64sha256
  layer_name       = "requirement_${var.account.account_mapping}"

  compatible_runtimes = ["python3.7"]

  lifecycle {
    ignore_changes = [
      source_code_hash
    ]
  }
}

data "local_file" "requirements" {
  filename = "../../lambda_functions/${var.openapi_version}/requirements/requirements.txt"
}

data "archive_file" "lambda_archive" {
  type        = "zip"
  source_dir  = "../../lambda_functions/${var.openapi_version}/functions/${local.lambda_underscore}"
  output_path = "./lambda_${local.lambda_underscore}.zip"
}

data "archive_file" "lambda_layer_archive" {
  type        = "zip"
  source_dir  = "../../lambda_functions/${var.openapi_version}/lambda_layers"
  output_path = "./lambda_layers_${local.lambda_underscore}_${substr(replace(base64sha256(data.local_file.requirements.content_base64), "/[^0-9A-Za-z_]/", ""), 0, 5)}.zip"
}
