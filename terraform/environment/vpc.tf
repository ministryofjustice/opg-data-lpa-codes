data "aws_subnet_ids" "private" {
  vpc_id = local.account.vpc_id

  filter {
    name   = "tag:Name"
    values = ["private-*"]
  }
}

data "aws_region" "region" {}
