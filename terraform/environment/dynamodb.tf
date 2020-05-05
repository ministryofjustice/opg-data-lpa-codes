resource "aws_dynamodb_table" "lpa_codes" {
  name         = "lpa-codes-${local.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "lpa"
  range_key    = "actor"

  attribute {
    name = "lpa"
    type = "S"
  }

  attribute {
    name = "actor"
    type = "S"
  }

  attribute {
    name = "code"
    type = "S"
  }

  global_secondary_index {
    name            = "identifier_index"
    hash_key        = "actor"
    range_key       = "code"
    projection_type = "KEYS_ONLY"
  }

  point_in_time_recovery {
    enabled = local.account.pit_recovery_flag
  }

  tags = local.default_tags
}
