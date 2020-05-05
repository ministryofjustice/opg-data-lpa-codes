resource "aws_dynamodb_table" "lpa-codes" {
  name         = "lpa-codes-${local.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "Id"
    type = "N"
  }

  attribute {
    name = "Code"
    type = "S"
  }

  tags = local.default_tags
}
