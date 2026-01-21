resource "aws_backup_vault" "data_lpa_codes" {
  name = "data-lpa-codes-backup-vault-${local.environment}"

  tags = local.default_tags
}

resource "aws_iam_role" "data_lpa_codes_backup_role" {
  name = "data-lpa-codes-backup-role-${local.environment}"

  assume_role_policy = data.aws_iam_policy_document.aws_backup_assume_role_policy.json
}

resource "aws_iam_role_policy" "data_lpa_codes_backup_policy" {
  name = "data-lpa-codes-backup-policy-${local.environment}"
  role = aws_iam_role.data_lpa_codes_backup_role.id

  policy = data.aws_iam_policy_document.data_lpa_codes_backup_policy.json
}

data "aws_iam_policy_document" "aws_backup_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["backup.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account.account_id]
    }
  }
}

data "aws_iam_policy_document" "data_lpa_codes_backup_policy" {
  statement {
    sid    = "AllowBackupOperations"
    effect = "Allow"
    actions = [
      "dynamodb:CreateBackup",
      "dynamodb:DescribeTable"
    ]
    resources = [
      aws_dynamodb_table.lpa_codes.arn,
      aws_dynamodb_table.data_lpa_codes.arn
    ]
  }

  statement {
    sid    = "AllowListing"
    effect = "Allow"
    actions = [
      "dynamodb:ListTables"
    ]
    resources = ["*"]
  }
}
