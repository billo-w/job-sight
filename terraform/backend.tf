terraform {
  required_version = ">= 1.0"

  backend "s3" {
    endpoint   = "nyc3.digitaloceanspaces.com"        # or your region endpoint
    bucket     = "job-sight-terraform"               # the Spaces bucket you created
    key        = "state/terraform.tfstate"           # path inside the bucket
    region     = "us-east-1"                         # any valid AWS region (ignored by DO)
    access_key = var.spaces_access_key
    secret_key = var.spaces_secret_key
    skip_region_validation      = true
    skip_credentials_validation = true
    force_path_style            = true
  }
}