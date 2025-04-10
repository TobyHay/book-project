# Folder for dashboard / visualisations
This folder contains a Streamlit dashboard that loads data from the RDS using psycopg2.
To run locally: `streamlit run dashboard.py`.

Also contains sub-folders:

* terraform/

# Dashboard - running locally
## Requirements

To install requirements run:
`pip install -r requirements.txt`

A .env file must contain these variables:

```
DB_HOST=
DB_NAME=
DB_USERNAME=
DB_PASSWORD=
DB_PORT=
```


Dashboard Wireframe:
![Dashboard Wireframe](../assets/dashboard_wireframe.png)




# Terraform

terraform/ - contains code for storage infrastructure

* main.tf

    * Creates an ECR repository for the dashboard docker image
    * Creates a security group for the dashboard
    * Specifies ingress-egress rules for the security group
    * Creates a CloudWatch log group for the ECS service
    * Creates a ECS task definition
    * Triggers an ECS service based on the task definition
    * Returns the ECR image uri's in the terminal once step 1 from below has finished running.

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

2. Once successful, run the commands below to create the ECR repository for the dashboard image:  
    * `terraform apply -target=aws_ecr_repository.c16-book-project-dashboard-ecr`

3. Copy the image uri outputted in the console from step 2 and paste the value into the corresponding variable in the `variables.tf` file

4. Carry out the steps below to add a Docker image to the new ECR repository that has been created under the heading ECR Image.

5. Run `terraform apply` once the previous step is complete to apply the rest of script.

Once the ECR repository has been set up with a Docker image, only step 5 is required to set up the infrastructure from now on.


# ECR Image

### **≤CONTAINS ALL THE STEPS REQUIRED TO SET UP THE DOCKER IMAGE FOR THE DASHBOARD DEPENDING ON FILE FORMAT TO BE CHANGED V≥**

#### ...
add_ecr/ - Contains code for setting up the lambda Docker image

This is an example folder for deploying a lambda script to AWS ECR. Two folders should be created that follow the same structure for both ECR repositories, containing:

* `Dockerfile` - which includes the commands required to convert the lambda function script into a Docker image

* `placeholder_image_for_ecr.py` - which is the lambda script to be converted into a Docker image.


## Get started

To set up the ECR repository with the lambda Docker image, carry out the following steps after carrying out steps 1 and 2 from the terraform section:

1. Replace the `placeholder_image_for_ecr.py` placeholder script with your lambda script

2. Replace `placeholder_image_for_ecr` in the `Dockerfile` on line 5 and 9 with the name of your script.

3. Follow the steps on [here](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions) to dockerise the python script.

4. Follow the push commands on the AWS console for the relevant ECR repository
#### ...