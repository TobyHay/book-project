variable "DB_USERNAME" {
  type=string
}

variable "DB_PASSWORD" {
  type=string
}

variable "DB_NAME" {
  type=string
}

variable "DB_PORT" {
  type=string
}

variable "DB_HOST" {
  type=string
}

variable "FROM_EMAIL" {
  type=string
}

variable "TO_EMAIL" {
  type=string
}

variable "c16-VPC" {
  type=string
  default = "vpc-0f7ba8057a52dd82d"
}

variable "state_machine_name" {
    type=string
    default = "c16-book-project-sfn"
}

variable "image_uri_for_lambda_function_1" {
    type=string
    default =  "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c16-book-project-write-to-rds-ecr"
}

variable "image_uri_for_lambda_function_2" {
    type=string
    default = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c16-book-project-create-email-ecr"
}