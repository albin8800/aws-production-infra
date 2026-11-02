# 1. Fetch the latest official Ubuntu 22.04 LTS AMI ID
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical's official AWS Account ID                                                                                                                                                                

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# 2. Automatically generate a secure SSH key in Terraform
resource "tls_private_key" "rsa" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "deployer" {
  key_name   = "production-deployer-key"
  public_key = tls_private_key.rsa.public_key_openssh
}

# 3. The Ubuntu EC2 Instance                                                                                                                                                                                                          
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro" # Free-tier eligible                                                                                                                                                                                     

  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  associate_public_ip_address = true
  key_name                    = aws_key_pair.deployer.key_name

  # Root SSD Disk (8GB gp3 is fully free-tier eligible)                                                                                                                                                                               
  root_block_device {
    volume_size           = 8
    volume_type           = "gp3"
    delete_on_termination = true
  }

  # User Data: Startup script that installs Nginx upon boot
  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y nginx
              systemctl enable nginx
              systemctl start nginx
              echo "<h1>Welcome to Production AWS Infrastructure!</h1><p>Provisioned with Terraform by Albin.</p>" > /var/www/html/index.html
              EOF

  tags = {
    Name = "production-web-server"
  }
}
