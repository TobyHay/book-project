# Folder for the database and related scripts
Contains sub-folders:
- terraform

# Terraform

## Prerequisites
Before running any Terraform script, please set up the AWS CLI on your device by inputting your AWS credentials. For more information, visit https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-envvars.html.

Please setup a file named `terraform.tfvars` that specifies environmental variables and follows this format:
```
DB_USERNAME=<your_database_username>
DB_PASSWORD=<your_database_password>
```
## Files

The Terraform files can be run using `terraform init` followed by `terraform apply`.

- terraform/ - Contains code for storage infrastructure
    - `main.tf` 
        - Creates RDS database 
        - Creates security group
        - Specifies Postgres ingress-egress rules
        - Returns the database address in the terminal once `terraform apply` has finished running.
        - returns`<db_ip_address>` in the terminal. 

    - `variables.tf`
        - allows for environmental variables to be passed into the main file (from the user-created file `terraform.tfvars`).


# Schema
The schema populates the database with tables once it has been created by the Terraform script.
Please run `psql -h <db_ip_address> -U books_project -d booksdb`, followed 
by the database password when prompted, to run the schema.
We have carefully specified column datatypes to meet the minimum requirements of our database. This allows it to run as 
efficiently as possible without sacrificing functionality. 