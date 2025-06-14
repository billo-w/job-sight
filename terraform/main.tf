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

resource "digitalocean_project" "project" {
  name        = "Job-Sight-Project"
  resources   = [digitalocean_app.app.urn]
}

 resource "digitalocean_container_registry" "app_registry" {
  name                   = "job-sight-app"
  subscription_tier_slug = "starter"
}

resource "digitalocean_app" "app" {
  spec {
    name = "job-sight-app"
    alert {
      rule = "DEPLOYMENT_FAILED"
    }

    service {
      name               = "job-sight"
      instance_count     = 1
      instance_size_slug = "apps-s-1vcpu-0.5gb"
      http_port          = 5000

      image {
        registry_type = "DOCR"
        repository    = "job-sight"
        tag           = "latest"
        deploy_on_push {
          enabled = true
        }
      }
      log_destination {
        name = "logtail"
        logtail {
          token = var.logtail_source_token
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
      env {
        key   = "DATABASE_URL"
        value = var.existing_database_url
      }
    }
  }
}