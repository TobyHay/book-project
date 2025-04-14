output "image_uri_for_dashboard" {
    value = aws_ecr_repository.c16-book-project-dashboard-ecr.repository_url
}