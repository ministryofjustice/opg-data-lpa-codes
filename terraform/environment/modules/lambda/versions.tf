terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.5.0"
    }
  }
}
