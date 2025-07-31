data "aws_availability_zones" "available" {
}

data "aws_subnet" "private" {
  count             = 3
  vpc_id            = local.account.vpc_id
  availability_zone = data.aws_availability_zones.available.names[count.index]

  filter {
    name = "tag:Name"
    values = [
      "application-*",
      "private-*"
    ]
  }
}

data "aws_region" "region" {}
