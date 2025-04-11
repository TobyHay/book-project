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

variable "c16-VPC" {
  type=string
  default = "vpc-0f7ba8057a52dd82d"
}

variable "ecs_name" {
    type=string
    default = "c16-book-project-dashboard"
}

variable "image_uri_for_dashboard" {
    type=string
    default =  "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c16-book-project-dashboard-ecr"
}