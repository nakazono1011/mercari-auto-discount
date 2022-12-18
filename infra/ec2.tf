resource "aws_instance" "app_server" {
  ami                    = "ami-046a961f907758d0d"
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.public_sg.id]
  subnet_id              = aws_subnet.public[0].id

  tags = {
    Name = "${var.env}-${var.app_name}-ec2-instance"
  }
}