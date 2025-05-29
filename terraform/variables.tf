variable "do_token" {}
variable "github_repo" {
  description = "GitHub repository in format user/repo; supplied via TF_VAR_github_repo"
}
variable "spaces_access_key" {
  type        = string
  description = "DigitalOcean Spaces access key (for remote state)"
}

variable "spaces_secret_key" {
  type        = string
  description = "DigitalOcean Spaces secret key (for remote state)"
}