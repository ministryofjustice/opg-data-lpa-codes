//===============Related to lpa_codes_api_gateway===================

//This gets attached on the lpa_codes_api_gateway directly (api_rest.tf)
data "aws_iam_policy_document" "resource_policy" {
  statement {
    sid    = "ApiAllowDigitalDeputyUsers"
    effect = "Allow"

    principals {
      identifiers = local.account.allowed_roles
      type        = "AWS"
    }

    actions = ["execute-api:Invoke"]

    // API Gateway will add all of the rest of the ARN details in for us. Prevents a circular dependency.
    resources = ["execute-api:/*/*/*"]
  }
}
