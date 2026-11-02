output "ec2_public_ip" {
  description = "The public IP address of our web server"
  value       = aws_instance.web.public_ip
}

output "ssh_connection_command" {
  description = "Command to SSH directly into the instance"
  value       = "ssh -i ~/.ssh/aws_production_key ubuntu@${aws_instance.web.public_ip}"
}
