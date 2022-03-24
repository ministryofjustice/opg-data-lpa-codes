resource "aws_api_gateway_stage" "currentstage" {
  stage_name           = var.openapi_version
  depends_on           = [aws_cloudwatch_log_group.lpa_codes]
  rest_api_id          = var.rest_api.id
  deployment_id        = aws_api_gateway_deployment.deploy.id
  xray_tracing_enabled = true
  tags                 = var.tags
  variables = {
    lpa_codes_function_name : var.lpa_codes_lambda.function_name
  }

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.lpa_codes.arn
    format = join("", [
      "{\"requestId\":\"$context.requestId\",",
      "\"ip\":\"$context.identity.sourceIp\"",
      "\"caller\":\"$context.identity.caller\"",
      "\"user\":\"$context.identity.user\"",
      "\"requestTime\":\"$context.requestTime\"",
      "\"httpMethod\":\"$context.httpMethod\"",
      "\"resourcePath\":\"$context.resourcePath\"",
      "\"status\":\"$context.status\"",
      "\"protocol\":\"$context.protocol\"",
      "\"responseLength\":\"$context.responseLength\"}"
    ])
  }
}

resource "aws_cloudwatch_log_group" "lpa_codes" {
  name              = "API-Gateway-Execution-Logs-${var.rest_api.name}-${var.openapi_version}"
  retention_in_days = 30
  tags              = var.tags
}

data "aws_wafv2_web_acl" "integrations" {
  name  = "integrations-${var.account_name}-${var.region_name}-web-acl"
  scope = "REGIONAL"
}

resource "aws_wafv2_web_acl_association" "api_gateway_stage" {
  resource_arn = aws_api_gateway_stage.currentstage.arn
  web_acl_arn  = data.aws_wafv2_web_acl.integrations.arn
}
