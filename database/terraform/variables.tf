variable "AWS_ACCESS_KEY_ID" {
  type = string
  description = "My AWS Access Key"
}
variable "AWS_SECRET_ACCESS_KEY" {
  type = string
  description = "My AWS Secret Access Key"
}

variable "DB_USERNAME" {
    type = string
    description = "database username"
}

variable "DB_PASSWORD" {
    type = string
    description = "database password"
}

variable "sigma_vpc_name" {
    type = string
    description = "VPC name"
    default = "c16-VPC"
}

variable "sigma_subnet_name" {
     type = string
     description = "Subnet name"
     default = "c16-public-subnet-group"
}
