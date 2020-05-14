resource "aws_dynamodb_table" "lpa_codes" {
  name         = "lpa-codes-${local.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "code"

  attribute {
    name = "code"
    type = "S"
  }

  attribute {
    name = "lpa"
    type = "S"
  }

  attribute {
    name = "actor"
    type = "S"
  }

  global_secondary_index {
    name            = "key_index"
    hash_key        = "actor"
    range_key       = "lpa"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = local.account.pit_recovery_flag
  }

  tags = local.default_tags
}
