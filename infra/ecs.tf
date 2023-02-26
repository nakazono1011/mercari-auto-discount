resource "aws_ecs_cluster" "selin" {
  name = "${var.env}-${var.app_name}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "chrome" {
  family                   = "${var.env}-${var.app_name}-chrome"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  container_definitions = jsonencode([
    {
      name = "${var.env}-${var.app_name}-chrome"
      "image" : "${aws_ecr_repository.selenium_server.repository_url}:latest",
      cpu       = 0
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
    }
  ])
  cpu                = 256
  memory             = 512
  execution_role_arn = "arn:aws:iam::445217156642:role/ecsTaskExecutionRole"
  task_role_arn      = "arn:aws:iam::445217156642:role/ecsTaskExecutionRole"
}

resource "aws_ecs_service" "chrome_service" {
  name            = "chrome_service"
  launch_type     = "FARGATE"
  cluster         = aws_ecs_cluster.selin.name
  task_definition = aws_ecs_task_definition.chrome.arn
  desired_count   = 1

  network_configuration {
    subnets          = toset(aws_subnet.public.*.id)
    assign_public_ip = true
  }
}
