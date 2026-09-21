data "archive_file" "userfunctions_lambda_zip" {
  source_dir  = "src/users/"
  output_path = "/tmp/userfunctions_lambda.zip"
  type        = "zip"
  depends_on  = [null_resource.build_dependencies]
}
