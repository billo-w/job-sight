provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "web" {
  image  = "ubuntu-22-04-x64"
  name   = "job-sight-droplet"
  region = "lon1"
  size   = "s-1vcpu-1gb"
  ssh_keys = [var.ssh_fingerprint]
}