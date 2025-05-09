# Folder for the email script and related scripts

Contains sub-folders:

* terraform/
* add_ecr/
* email_script/

# Terraform

terraform/ - contains code for storage infrastructure

* main.tf

    * Creates 2 ECR repositories for the lambda docker images
    * Creates a security group
    * Specifies ingress-egress rules for the security group
    * Sets up the IAM roles for all the resources
    * Creates a CloudWatch log group for both resources
    * Creates 2 Lambda Functions
    * Creates a AWS Step Function
    * Creates a AWS EventBridge Schedule
    * Returns the ECR image uri's in the terminal once step 1 from above has finished running.

* variables.tf 

    * allows for environmental variables to be passed into the main file.

* outputs.tf 

    * allows for the image uri's to be returned to the terminal when performing step 1 above

Please setup a third file, `terraform.tfvars`, that specifies environmental variables and follows this format:

```
DB_USERNAME=<your_database_username>
DB_PASSWORD=<your_database_password>
DB_PORT=5432
DB_NAME=<your_database_name>
DB_HOST=<your_database_address>
```

This configuration assumes that AWS CLI has been set up and so AWS keys are not required within the `terraform.tfvars`. If you haven't set up the AWS CLI, you can follow up to step 3 from this [article](https://medium.com/@simonazhangzy/installing-and-configuring-the-aws-cli-7d33796e4a7c) to help you.


## Get started

The Terraform files can be run using the following steps for the first time:

1. Run `terraform init`

2. Once successful, run both of the commands below:  
    * `terraform apply -target=aws_ecr_repository.c16-book-project-write-to-rds-ecr`
    * `terraform apply -target=aws_ecr_repository.c16-book-project-create-email-ecr`

3. Copy the image uri for each lambda function that is outputted by step 2 and paste the value into the corresponding variable in the `variables.tf` file

4. Carry out the steps within the ['Get Started'](#get-started-1) section below to add a Docker image to the new ECR repositories that have been created in step 2.

5. Run `terraform apply` once complete to apply the rest of script.

Once the ECR repository has been set up with a Docker image, only step 5 is required to set up the infrastructure from now on.


# ECR Images

add_ecr/ - Contains code for setting up the lambda Docker image

This is an example folder for deploying a lambda script to AWS ECR. Two folders should be created that follow the same structure for both ECR repositories, containing:

* `Dockerfile` - which includes the commands required to convert the lambda function script into a Docker image

* `email_sender.py` - which is the lambda script to be converted into a Docker image.


## IMPORTANT

- NOTE: YOUR ACCOUNT MUST BE EXITED FROM SANDBOX MODE IN ORDER TO SEND EMAILS THAT ARE NOT VERIFIED ON YOUR AWS. TO EXIT SANDBOX FOLLOW: https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html?icmpid=docs_ses_console 


## Get started <a name="dockerise_image"></a>

To set up the ECR repository with the lambda Docker image, carry out the following steps after carrying out steps 1 and 2 from the terraform section:


1. Set up a .env of format:

```
DB_USERNAME=
DB_PASSWORD=
DB_PORT=
DB_NAME=
DB_HOST=
ACCESS_KEY=
SECRET_KEY=
```

2. Follow the steps on [here](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions) to dockerise the python script, making sure to use the ` --env-file .env` flag for docker build.

3. Follow the push commands on the AWS console for the relevant ECR repository

