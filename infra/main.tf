provider "aws" {
  region  = "ap-northeast-1"
  profile = "myaws"

  default_tags {
    tags = {
      Env       = "dev"
      ManagedBy = "Terraform"
    }
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    profile = "myaws"
    bucket  = "myaws-tfstate"
    region  = "ap-northeast-1"
    key     = "terraform.tfstate"
    encrypt = true
  }
}
