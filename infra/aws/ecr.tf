locals {
  ecr-lifecycle-policy = {
    rules = [
      {
        action = {
          type = "expire"
        }
        description  = "最新の5つを残してイメージを削除する"
        rulePriority = 1
        selection = {
          countNumber = 5
          countType   = "imageCountMoreThan"
          tagStatus   = "any"
        }
      },
    ]
  }
}


resource "aws_ecr_repository" "selenium_server" {
  name                 = "${var.env}-${var.app_name}-selenium-server"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

}

resource "aws_ecr_lifecycle_policy" "selenium" {
  repository = aws_ecr_repository.selenium_server.name
  policy     = jsonencode(local.ecr-lifecycle-policy)
}