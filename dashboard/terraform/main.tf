terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.32.0"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "eu-west-2"
}



# ECRs
resource "aws_ecr_repository" "c16-book-project-dashboard-ecr" {
  name                 = "${var.ecs_name}-ecr"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# NETWORKING
data "aws_vpc" "c16-vpc" {
    id = var.c16-VPC
}

data "aws_subnets" "selected" {
  filter {
    name   = "tag:Name"
    values = [ "c16-public-subnet-2", "c16-public-subnet-1", "c16-public-subnet-3" ]
  }
}

resource "aws_security_group" "c16-book-project-dashboard-sg" {
    name = "${var.ecs_name}-sg"
    vpc_id = var.c16-VPC
}

resource "aws_vpc_security_group_ingress_rule" "read_from_database_ipv4" {
    security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
    cidr_ipv4 = "0.0.0.0/0"
    from_port = tonumber(var.DB_PORT)
    to_port = tonumber(var.DB_PORT)
    ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "read_from_database_ipv6" {
    security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
    cidr_ipv6 = "::/0"
    from_port = tonumber(var.DB_PORT)
    to_port = tonumber(var.DB_PORT)
    ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "allow_access_to_dashboard_ipv4" {
    security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
    cidr_ipv4 = "0.0.0.0/0"
    from_port = 8501
    to_port = 8501
    ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "allow_access_to_dashboard_ipv6" {
  security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
  cidr_ipv6 = "::/0"
  from_port = 8501
  to_port = 8501
  ip_protocol = "tcp" 
}

resource "aws_vpc_security_group_egress_rule" "read_from_database_ipv4" {
    security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
    cidr_ipv4 = "0.0.0.0/0"
    from_port = tonumber(var.DB_PORT)
    to_port = tonumber(var.DB_PORT)
    ip_protocol = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "read_from_database_ipv6" {
    security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
    cidr_ipv6 = "::/0"
    from_port = tonumber(var.DB_PORT)
    to_port = tonumber(var.DB_PORT)
    ip_protocol = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "allow_access_to_dashboard_ipv4" {
    security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
    cidr_ipv4 = "0.0.0.0/0"
    from_port = 8501
    to_port = 8501
    ip_protocol = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "allow_access_to_dashboard_ipv6" {
  security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
  cidr_ipv6 = "::/0"
  from_port = 8501
  to_port = 8501
  ip_protocol = "tcp" 
}

resource "aws_vpc_security_group_egress_rule" "allow_access_for_aws_ecs_ipv6" {
  security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
  cidr_ipv6 = "::/0"
  from_port = 443
  to_port = 443
  ip_protocol = "tcp" 
}

resource "aws_vpc_security_group_egress_rule" "allow_access_for_aws_ecs_ipv4" {
  security_group_id = aws_security_group.c16-book-project-dashboard-sg.id
  cidr_ipv4 = "0.0.0.0/0"
  from_port = 443
  to_port = 443
  ip_protocol = "tcp" 
}

# LOGGING
resource "aws_cloudwatch_log_group" "c16-book-project-dashboard-lg" {
  name = "/ecs/${var.ecs_name}"
  retention_in_days = 0
}

resource "aws_cloudwatch_log_stream" "c16-book-project-dashboard-ls" {
  name           = "ecs/${var.ecs_name}/"
  log_group_name = aws_cloudwatch_log_group.c16-book-project-dashboard-lg.name
}


# ECS TASK DEFINITION
data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "c16-book-project-dashboard-td" {
    family = aws_ecr_repository.c16-book-project-dashboard-ecr.name
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    cpu = 512
    memory = 1024
    execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
    container_definitions = jsonencode([{
        name      = var.ecs_name
        image     = var.image_uri_for_dashboard
        essential = true
        environment = [
            {
                name = "DB_HOST"
                value = var.DB_HOST
            },
            {
                name = "DB_NAME"
                value = var.DB_NAME
            },
            {
                name = "DB_USERNAME"
                value = var.DB_USERNAME
            },
            {
                name = "DB_PASSWORD"
                value = var.DB_PASSWORD
            },
            {
                name = "DB_PORT"
                value = var.DB_PORT
            }]
        portMappings = [
            {
            containerPort = 8501
            hostPort      = 8501
            }
        ]
        logConfiguration = {
            logDriver = "awslogs",
            options = {
                awslogs-group = "${aws_cloudwatch_log_group.c16-book-project-dashboard-lg.name}",
                awslogs-region = "eu-west-2",
                awslogs-stream-prefix = "ecs"
                }
            }
        }
    ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture = "X86_64"
  }
}

data "aws_ecs_cluster" "c16-ecs-cluster" {
  cluster_name = "c16-ecs-cluster"
}



# ECS SERVICE
resource "aws_ecs_service" "c16-book-project-dashboard" {
  name            = "${var.ecs_name}-ecs-service"
  cluster         = data.aws_ecs_cluster.c16-ecs-cluster.id
  task_definition = aws_ecs_task_definition.c16-book-project-dashboard-td.arn
  desired_count   = 1
  launch_type = "FARGATE"

  network_configuration {
    assign_public_ip = true
    security_groups  = [aws_security_group.c16-book-project-dashboard-sg.id]
    subnets          = data.aws_subnets.selected.ids
  }
}