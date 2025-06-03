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
    }
  }
}