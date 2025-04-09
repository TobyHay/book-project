terraform {
    required_providers {
      aws = { 
        source = "hashicorp/aws"
        version = "~>5.93.0"
      }
    }
}


provider "aws" {
    region = "eu-west-2"
}

data "aws_vpc" "c16_vpc" {
    filter {    
        name = "tag:Name"
        values = [var.sigma_vpc_name]
    }
}

resource "aws_security_group" "c16-books-db-sg" {
    name = "c16-books-db-sg"
    description = "security group for the books database"
    vpc_id = data.aws_vpc.c16_vpc.id
    tags = {
        Name = "c16-books-db-sg"
    }
}


resource "aws_vpc_security_group_ingress_rule" "postgres" {
    security_group_id = aws_security_group.c16-books-db-sg.id
    ip_protocol = "tcp"
    from_port = 5432
    to_port = 5432
    cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "all_traffic" {
    security_group_id = aws_security_group.c16-books-db-sg.id
    cidr_ipv4 = "0.0.0.0/0"
    ip_protocol = "-1"
}

resource "aws_db_instance" "c16-books-db" {
    identifier = "c16-books-db"
    db_name = "booksdb"
    engine = "postgres"
    engine_version = "17.2"
    allocated_storage = 20
    instance_class = "db.t4g.micro"
    username = var.DB_USERNAME
    password = var.DB_PASSWORD
    vpc_security_group_ids = [aws_security_group.c16-books-db-sg.id]
    db_subnet_group_name = var.sigma_subnet_name
    publicly_accessible = true
    skip_final_snapshot = true
    license_model = "postgresql-license"
    performance_insights_enabled = false
}

output "db_ip_address" {
    description = "db address"
    value = aws_db_instance.c16-books-db.endpoint
}
