resource "aws_dynamodb_table" "lpa_codes" {
  name                        = "lpa-codes-${local.environment}"
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "code"
  stream_enabled              = true
  stream_view_type            = "NEW_AND_OLD_IMAGES"
  deletion_protection_enabled = local.environment == "development" ? false : true

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

  ttl {
    attribute_name = "expiry_date"
    enabled        = true
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

resource "aws_dynamodb_table" "data_lpa_codes" {
  name                        = "data-lpa-codes-${local.environment}"
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "PK"
  stream_enabled              = true
  stream_view_type            = "NEW_AND_OLD_IMAGES"
  deletion_protection_enabled = local.environment == "development" ? false : true

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "ActorLPA"
    type = "S"
  }

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  global_secondary_index {
    name            = "ActorLPAIndex"
    hash_key        = "ActorLPA"
    range_key       = "PK"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = local.account.pit_recovery_flag
  }

  tags = local.default_tags
}
