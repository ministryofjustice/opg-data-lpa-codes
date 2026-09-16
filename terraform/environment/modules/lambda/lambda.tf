locals {
  lambda          = "${var.lambda_prefix}-${var.environment}-${var.openapi_version}"
  lambda_dbstream = "${var.lambda_prefix}-dbstream-${var.environment}-${var.openapi_version}"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name = "/aws/lambda/${local.lambda}"
}

resource "aws_cloudwatch_log_group" "lambda_dbstream" {
  name = "/aws/lambda/${local.lambda_dbstream}"
}

resource "aws_cloudwatch_log_group" "outbound_event_bus" {
  name              = "/aws/events/${var.outbound_event_bus}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_resource_policy" "eventbridge_to_logs" {
  policy_name = "${var.lambda_prefix}-${var.environment}-eventbridge-to-logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowEventBridgeToWriteToLogs"
      Effect = "Allow"
      Principal = {
        Service = "events.amazonaws.com"
      }
      Action = [
        "logs:CreateLogStream",
        "logs:PutLogEvents",
      ]
      Resource = aws_cloudwatch_log_group.outbound_event_bus.arn
      Condition = {
        ArnEquals = {
          "AWS:SourceArn" = aws_cloudwatch_event_rule.activation_key_used.arn
        }
      }
    }]
  })
}

resource "aws_cloudwatch_event_rule" "activation_key_used" {
  name           = "${var.lambda_prefix}-${var.environment}-activation-key-used"
  description    = "Capture activation-key-used events and send them to CloudWatch Logs"
  event_bus_name = var.outbound_event_bus

  event_pattern = jsonencode({
    source        = ["opg.poas.use"]
    "detail-type" = ["activation-key-used"]
  })
}

resource "aws_cloudwatch_event_target" "activation_key_used_logs" {
  rule           = aws_cloudwatch_event_rule.activation_key_used.name
  event_bus_name = aws_cloudwatch_event_rule.activation_key_used.event_bus_name
  target_id      = "activation-key-used-cloudwatch-logs"
  arn            = aws_cloudwatch_log_group.outbound_event_bus.arn
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
      LOGGER_LEVEL       = var.logger_level
      ENVIRONMENT        = var.environment
      OUTBOUND_EVENT_BUS = var.outbound_event_bus
    }
  }

  logging_config {
    log_format = "JSON"
  }

  tracing_config {
    mode = "Active"
  }
}

resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowApiLPACodesGatewayInvoke-${var.environment}-${var.openapi_version}-${var.lambda_prefix}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${var.rest_api.execution_arn}/*/*/*"
}
