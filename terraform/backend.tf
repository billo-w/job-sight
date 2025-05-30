terraform {
  required_version = ">= 1.0"

  backend "s3" {
    endpoint                    = "https://lon1.digitaloceanspaces.com" # Corrected: Generic DO Spaces endpoint for the region
    bucket                      = "job-sight-terraform"
    key                         = "terraform.tfstate"
    region                      = "us-east-1" # Or try your specific DO region like 'lon1' if supported
    skip_region_validation      = true
    skip_credentials_validation = true
    use_path_style              = true
    skip_requesting_account_id  = true
    workspace_key_prefix        = ""
  }
}