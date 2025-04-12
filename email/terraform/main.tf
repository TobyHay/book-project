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
resource "aws_ecr_repository" "c16-book-project-write-to-rds-ecr" {
  name                 = "c16-book-project-write-to-rds-ecr"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c16-book-project-create-email-ecr" {
  name                 = "c16-book-project-create-email-ecr"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}


# NETWORKING
data "aws_vpc" "c16-vpc" {
    id = var.c16-VPC
}

data "aws_subnets" "c16-public-subnets" {
  filter {
    name   = "tag:Name"
    values = [ "c16-public-subnet-2", "c16-public-subnet-1", "c16-public-subnet-3" ]
  }
}

resource "aws_security_group" "c16-book-project-sg" {
    name = "c16-book-project-sg"
    vpc_id = var.c16-VPC
}

resource "aws_vpc_security_group_ingress_rule" "allow_access_to_scrape_data" {
    security_group_id = aws_security_group.c16-book-project-sg.id
    cidr_ipv4 = "0.0.0.0/0"
    from_port = 443
    to_port = 443
    ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "allow_access_to_database" {
  security_group_id = aws_security_group.c16-book-project-sg.id
  cidr_ipv4 = "0.0.0.0/0"
  from_port = tonumber(var.DB_PORT)
  to_port = tonumber(var.DB_PORT)
  ip_protocol = "tcp" 
}

resource "aws_vpc_security_group_egress_rule" "allow_access_to_send_emails_ipv6" {
  security_group_id = aws_security_group.c16-book-project-sg.id
  cidr_ipv6 = "::/0"
  from_port = 0
  to_port = 65535
  ip_protocol = "tcp" 
}

resource "aws_vpc_security_group_egress_rule" "allow_access_to_send_emails_ipv4" {
  security_group_id = aws_security_group.c16-book-project-sg.id
  cidr_ipv4 = "0.0.0.0/0"
  from_port = 0
  to_port = 65535
  ip_protocol = "tcp" 
}



# IAM for LAMBDA FUNCTION

data "aws_iam_policy_document" "assume_role_lambda" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda_book_project" {
  name               = "iam_for_lambda_book_project"
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}


data "aws_iam_policy_document" "lambda_policy_doc_for_book_project" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "ec2:DescribeNetworkInterfaces",
        "ec2:CreateNetworkInterface",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeInstances",
        "ec2:AttachNetworkInterface"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "lambda_logging_policy_for_book_project" {
  name        = "lambda_logging_policy_for_book_project"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_policy_doc_for_book_project.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda_book_project.name
  policy_arn = aws_iam_policy.lambda_logging_policy_for_book_project.arn
}


# CLOUDWATCH GROUPS FOR BOTH LAMBDA'S

resource "aws_cloudwatch_log_group" "c16-book-project-write-to-rds-lg" {
  name              = "/aws/lambda/c16-book-project-write-to-rds-lg"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "c16-book-project-create-email-lg" {
  name              = "/aws/lambda/c16-book-project-create-email-lg"
  retention_in_days = 14
}


# LAMBDA FUNCTIONS

resource "aws_lambda_function" "c16-book-project-write-to-rds-lg" {
  function_name = "c16-book-project-write-to-rds-lg"
  package_type = "Image"
  image_uri    = "${var.image_uri_for_lambda_function_1}:latest"
  role = aws_iam_role.iam_for_lambda_book_project.arn

  timeout      = 15
  memory_size  = 128

  vpc_config {
    subnet_ids         = data.aws_subnets.c16-public-subnets.ids
    security_group_ids = [aws_security_group.c16-book-project-sg.id]  
  }

  environment {
    variables = {
      DB_HOST     = var.DB_HOST
      DB_USER     = var.DB_USERNAME
      DB_PASSWORD = var.DB_PASSWORD
      DB_NAME     = var.DB_NAME
      DB_PORT = var.DB_PORT
    }
  }

  logging_config {
        log_format = "Text"
        log_group = aws_cloudwatch_log_group.c16-book-project-write-to-rds-lg.name
    }
    
    depends_on = [
        aws_iam_role_policy_attachment.lambda_logs,
        aws_cloudwatch_log_group.c16-book-project-write-to-rds-lg,
    ]
}

resource "aws_lambda_function" "c16-book-project-create-email-lg" {
  function_name = "c16-book-project-create-email-lg"
  package_type = "Image"
  image_uri    = "${var.image_uri_for_lambda_function_2}:latest"
  role = aws_iam_role.iam_for_lambda_book_project.arn

  timeout      = 15
  memory_size  = 128

  vpc_config {
    subnet_ids         = data.aws_subnets.c16-public-subnets.ids
    security_group_ids = [aws_security_group.c16-book-project-sg.id]  
  }

  environment {
    variables = {
      DB_HOST     = var.DB_HOST
      DB_USER     = var.DB_USERNAME
      DB_PASSWORD = var.DB_PASSWORD
      DB_NAME     = var.DB_NAME
      DB_PORT = var.DB_PORT
    }
  }

  logging_config {
        log_format = "Text"
        log_group = aws_cloudwatch_log_group.c16-book-project-create-email-lg.name
    }
    
    depends_on = [
        aws_iam_role_policy_attachment.lambda_logs,
        aws_cloudwatch_log_group.c16-book-project-create-email-lg,
    ]
}


# IAM of STATE MACHINE

data "aws_iam_policy_document" "assume_role_state_machine" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "state_machine" {
  name               = "c16-state-machine-book-project"
  assume_role_policy = data.aws_iam_policy_document.assume_role_state_machine.json
}

data "aws_iam_policy_document" "state_machine_run" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = ["${aws_lambda_function.c16-book-project-write-to-rds-lg.arn}", "${aws_lambda_function.c16-book-project-create-email-lg.arn}"]
  }

  statement {
    effect = "Allow"
    actions = ["ses:SendEmail"]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = ["logs:CreateLogDelivery",
                "logs:CreateLogStream",
                "logs:GetLogDelivery",
                "logs:UpdateLogDelivery",
                "logs:DeleteLogDelivery",
                "logs:ListLogDeliveries",
                "logs:PutLogEvents",
                "logs:PutResourcePolicy",
                "logs:DescribeResourcePolicies",
                "logs:DescribeLogGroups"
            ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "state_machine_run_role" {
  name   = "state_machine_run_role"
  role   = aws_iam_role.state_machine.id
  policy = data.aws_iam_policy_document.state_machine_run.json
}



# STEP FUNCTION/ STATE MACHINE

resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = var.state_machine_name
  role_arn = aws_iam_role.state_machine.arn
  publish = false

  definition = <<EOF
{
  "Comment": "The definition of the state machine using JSONata to run the daily write to the RDS and then send an email to subscribers",
  "QueryLanguage": "JSONata",
  "StartAt": "WriteToRDS",
  "States": {
    "WriteToRDS": {
      "Type": "Task",
      "Assign": {
        "result" : "{% $states.result.statusCode %}" 
        },
      "Resource": "${aws_lambda_function.c16-book-project-write-to-rds-lg.arn}",
      "Next": "ChoiceState"
    },
    "ChoiceState": {
      "Type": "Choice",
      "Default": "FailureState",
      "Choices": [
        {
          "Next": "CreateEmailState",
          "Condition": "{% $result = 200 %}"
        }
      ]
    },
    "CreateEmailState": {
      "Type" : "Task",
      "Resource": "${aws_lambda_function.c16-book-project-create-email-lg.arn}",
      "End": true
    },

    "FailureState": {
      "Type": "Fail",
      "Error": "DefaultStateError",
      "Cause": "Failed to scrape data and upload to RDS!"
    }
  }
}
EOF
}