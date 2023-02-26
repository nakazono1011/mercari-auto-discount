variable "env" {
  default = "dev"
}

variable "app_name" {
  default = "sellin"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  default = ["10.0.10.0/24", "10.0.20.0/24"]
}

variable "availability_zone" {
  default = ["ap-northeast-1a", "ap-northeast-1c"]
}

variable "private_subnet_cidr" {
  default = ["10.0.100.0/24", "10.0.200.0/24"]
}

variable "cidr_block-internet_gw" {
  default = "0.0.0.0/0"
}

variable "aws_amis" {
  type = map(any)
  default = {
    "us-east-1" = "ami-0739f8cdb239fe9ae"
    "us-west-2" = "ami-008b09448b998a562"
    "us-east-2" = "ami-0ebc8f6f580a04647"
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}