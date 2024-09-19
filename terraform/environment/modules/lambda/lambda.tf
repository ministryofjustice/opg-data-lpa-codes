locals {
  lambda            = "${var.lambda_prefix}-${var.environment}-${var.openapi_version}"
  lambda_dbstream   = "${var.lambda_prefix}-dbstream-${var.environment}-${var.openapi_version}"
  lambda_underscore = replace(var.lambda_prefix, "-", "_")
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
  package_type  = var.package_type
  role          = aws_iam_role.lambda_role.arn
  timeout       = var.timeout
  depends_on    = [aws_cloudwatch_log_group.lambda]

  image_uri = var.package_type != "Image" ? null : var.image_uri

  filename         = var.package_type != "Zip" ? null : data.archive_file.lambda_archive.output_path
  source_code_hash = var.package_type != "Zip" ? null : data.archive_file.lambda_archive.output_base64sha256
  handler          = var.package_type != "Zip" ? null : var.handler
  runtime          = var.package_type != "Zip" ? null : var.runtime
  layers           = var.package_type != "Zip" ? null : [aws_lambda_layer_version.lambda_layer.arn]
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
  logging_config {
    log_format = "JSON"
  }
  tracing_config {
    mode = "Active"
  }
  tags = var.tags
}


resource "aws_lambda_function" "lambda_dbstream_function" {
  function_name = local.lambda_dbstream
  role          = aws_iam_role.lambda_role.arn
  package_type  = var.package_type
  timeout       = 5
  depends_on    = [aws_cloudwatch_log_group.lambda_dbstream]

  image_uri = var.package_type != "Image" ? null : var.dbstream_image_uri

  filename         = var.package_type != "Zip" ? null : data.archive_file.lambda_dynamodb_stream_archive.output_path
  source_code_hash = var.package_type != "Zip" ? null : data.archive_file.lambda_dynamodb_stream_archive.output_base64sha256
  handler          = var.package_type != "Zip" ? null : var.dbstream_handler
  runtime          = var.package_type != "Zip" ? null : var.runtime

  vpc_config {
    subnet_ids         = var.aws_subnet_ids
    security_group_ids = [data.aws_security_group.lambda_api_ingress.id]
  }
  environment {
    variables = {
      API_VERSION = var.openapi_version
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

resource "aws_lambda_event_source_mapping" "dynamodb_stream_map" {
  event_source_arn  = var.dynamodb_table.stream_arn
  function_name     = aws_lambda_function.lambda_dbstream_function.arn
  starting_position = "LATEST"
}

resource "aws_lambda_layer_version" "lambda_layer" {
  filename         = data.archive_file.lambda_layer_archive.output_path
  source_code_hash = data.archive_file.lambda_layer_archive.output_base64sha256
  layer_name       = "requirement_${var.account.account_mapping}"

  compatible_runtimes = ["python3.8"]

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
  type = "zip"
  #  source_dir  = "../../lambda_functions/${var.openapi_version}/functions/${local.lambda_underscore}"
  source_dir  = "../../lambda_functions/${var.openapi_version}/functions/lpa_codes"
  output_path = "./lambda_${local.lambda_underscore}.zip"
}

data "archive_file" "lambda_dynamodb_stream_archive" {
  type = "zip"
  #  source_dir  = "../../lambda_functions/${var.openapi_version}/functions/${local.lambda_underscore}_dynamodb_streams"
  source_dir  = "../../lambda_functions/${var.openapi_version}/functions/lpa_codes_dynamodb_streams"
  output_path = "./lambda_lpa_dynamodb_streams_${var.openapi_version}.zip"
}

data "archive_file" "lambda_layer_archive" {
  type        = "zip"
  source_dir  = "../../lambda_functions/${var.openapi_version}/lambda_layers"
  output_path = "./lambda_layers_${local.lambda_underscore}_${substr(replace(base64sha256(data.local_file.requirements.content_base64), "/[^0-9A-Za-z_]/", ""), 0, 5)}.zip"
}
