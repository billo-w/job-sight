terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_app" "web_app" {
  spec {
    name = "job-sight-app"
    service {
      name = "web"
      github {  
        branch         = "main"
        deploy_on_push = true
        repo           = var.github_repo  
      }
      dockerfile_path = "./Dockerfile"
      http_port = 5000
      instance_size_slug = "basic-xxs"
      instance_count     = 1
    }
  }
}