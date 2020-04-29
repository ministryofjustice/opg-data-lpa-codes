data "aws_sns_topic" "rest_api" {
  name = "rest-api"
}

resource "aws_cloudwatch_metric_alarm" "rest_api_4xx_errors" {
  actions_enabled     = true
  alarm_actions       = [data.aws_sns_topic.rest_api.arn]
  alarm_description   = "Number of 4XX Errors returned for LPA Codes Rest API in ${terraform.workspace}"
  alarm_name          = "${local.environment}-rest-api-4xx-errors"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = 2
  dimensions = {
    ApiName = "lpa-codes-${terraform.workspace}"
  }
  evaluation_periods        = 5
  insufficient_data_actions = []
  metric_name               = "4XXError"
  namespace                 = "AWS/ApiGateway"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.account.threshold
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "rest_api_5xx_errors" {
  actions_enabled     = true
  alarm_actions       = [data.aws_sns_topic.rest_api.arn]
  alarm_description   = "Number of 5XX Errors returned for LPA Codes Rest API in ${terraform.workspace}"
  alarm_name          = "${local.environment}-rest-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = 2
  dimensions = {
    ApiName = "lpa-codes-${terraform.workspace}"
  }
  evaluation_periods        = 5
  insufficient_data_actions = []
  metric_name               = "5XXError"
  namespace                 = "AWS/ApiGateway"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.account.threshold
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "rest_api_high_count" {
  actions_enabled     = true
  alarm_actions       = [data.aws_sns_topic.rest_api.arn]
  alarm_description   = "Number of requests for LPA Codes Rest API in ${terraform.workspace}"
  alarm_name          = "${local.environment}-rest-api-high-count"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = 1
  dimensions = {
    ApiName = "lpa-codes-${terraform.workspace}"
  }
  evaluation_periods        = 1
  insufficient_data_actions = []
  metric_name               = "Count"
  namespace                 = "AWS/ApiGateway"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = 500
  treat_missing_data        = "notBreaching"
}
