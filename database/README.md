# Folder for the database and related scripts
Contains sub-folders:
- terraform

# Terraform

The Terraform files can be run using `terraform init` followed by `terraform apply`.

- terraform/ - Contains code for storage infrastructure
    - `main.tf` 
        - Creates RDS database 
        - Creates security group
        - Specifies Postgres ingress-egress rules
        - Returns the database address in the terminal once `terraform apply` has finished running.

    - `variables.tf`
        - allows for environmental variables to be passed into the main file.

Please setup a third file, `terraform.tfvars`, that specifies environmental variables and follows this format:
```
AWS_ACCESS_KEY_ID=<your_personal_aws_access_key_id>
AWS_SECRET_ACCESS_KEY=<your_personal_secret_access_key>
DB_USERNAME=<your_database_username>
DB_PASSWORD=<your_database_password>
```
