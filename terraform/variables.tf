variable "do_token" {
  description = "DigitalOcean API token for App Platform & Spaces"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "GitHub repo in format user/repo"
  type        = string
}

variable "adzuna_id" {
  description = "Adzuna API Application ID"
  type        = string
  sensitive   = true
}

variable "adzuna_key" {
  description = "Adzuna API Key"
  type        = string
  sensitive   = true
}

variable "foundry_endpoint" {
  description = "Azure Foundry service endpoint URL"
  type        = string
}

variable "foundry_key" {
  description = "Azure Foundry API key"
  type        = string
  sensitive   = true
}

variable "logtail_source_token" {
  description = "Logtail source token for logging"
  type        = string
  sensitive   = true
}

