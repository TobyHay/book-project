output "image_uri_for_lambda_function_1" {
    value=aws_ecr_repository.c16-book-project-write-to-rds-ecr.repository_url
}

output "image_uri_for_lambda_function_2" {
    value=aws_ecr_repository.c16-book-project-create-email-ecr.repository_url
}