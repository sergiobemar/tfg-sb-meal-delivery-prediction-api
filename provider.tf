# Specify the provider (GCP, AWS, Azure)
provider "google" {
	credentials = "credentials.json"
	project = "phonic-botany-288716"
	region = "europe-west1"
}