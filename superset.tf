resource "google_compute_instance" "default" {
  name         	= "superset"
  description	= "This template is used to create app server instances."
  machine_type 	= "e2-medium"
  zone         	= "europe-west1-b"

  tags = ["http-server"]

  boot_disk {
    initialize_params {
	  size 	= "15"
	  type 	= "pd-standard"
      image = "ubuntu-os-cloud/ubuntu-1804-lts"
    }
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral IP
    }
  }

  metadata = {
    name = "superset"
  }

  metadata_startup_script = file("./start_terraform.sh")
}

resource "google_compute_firewall" "http-server" {
  name    = "default-allow-http-terraform"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "8088"]
  }

  // Allow traffic from everywhere to instances with an http-server tag
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]
}

output "ip" {
  value = "${google_compute_instance.default.network_interface.0.access_config.0.nat_ip}"
}