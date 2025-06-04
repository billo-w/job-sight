terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token       = var.do_token
}

resource "digitalocean_app" "app" {
  spec {
    name = "job-sight-app"
    alert {
      rule = "DEPLOYMENT_FAILED"
    }

    service {
      name               = "job-container"
      instance_count     = 1
      instance_size_slug = "apps-s-1vcpu-0.5gb"
      http_port          = 5000

      image {
        registry_type = "DOCR"
        repository    = "job-container"
        tag           = "latest"
        deploy_on_push {
          enabled = true
        }
      }
      env {
        key   = "ADZUNA_ID"
        value = var.adzuna_id
      }
      env {
        key   = "ADZUNA_KEY"
        value = var.adzuna_key
      }
      env {
        key   = "FOUNDRY_ENDPOINT"
        value = var.foundry_endpoint
      }
      env {
        key   = "FOUNDRY_KEY"
        value = var.foundry_key
      }
      env {
        key   = "LOGTAIL_SOURCE_TOKEN"
        value = var.logtail_source_token
      }
    }
  }
}