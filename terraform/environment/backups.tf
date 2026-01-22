resource "aws_backup_vault" "data_lpa_codes" {
  name = "data-lpa-codes-backup-vault-${local.environment}"

  tags = local.default_tags
}

resource "aws_backup_plan" "data_lpa_codes" {
  count = local.account.backups_enabled ? 1 : 0
  name  = "data-lpa-codes-backup-plan-${local.environment}"

  rule {
    completion_window = 10080
    rule_name         = "DailyBackups"
    schedule          = "cron(0 5 ? * * *)"
    start_window      = 480
    target_vault_name = aws_backup_vault.data_lpa_codes.name

    lifecycle {
      cold_storage_after = 0
      delete_after       = 7
    }
  }

  rule {
    completion_window   = 10080
    recovery_point_tags = {}
    rule_name           = "Monthly"
    schedule            = "cron(0 5 1 * ? *)"
    start_window        = 480
    target_vault_name   = aws_backup_vault.data_lpa_codes.name

    lifecycle {
      cold_storage_after = 0
      delete_after       = 30
    }
  }
}

resource "aws_backup_selection" "data_lpa_codes" {
  count        = local.account.backups_enabled ? 1 : 0
  name         = "data-lpa-codes-backup-selection-${local.environment}"
  iam_role_arn = aws_iam_role.data_lpa_codes_backup_role.arn
  plan_id      = aws_backup_plan.data_lpa_codes[0].id

  resources = [
    aws_dynamodb_table.lpa_codes.arn,
    aws_dynamodb_table.data_lpa_codes.arn
  ]
}
