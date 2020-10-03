# CREATE VM ENGINE MACHINE WITH TERRAFORM

## Step 1. Downloading, installing and configuring Terraform

It's necessary to download the stable package of Terraform, then it's moved to ```/usr/local/bin```. Introduce the following commands into the Cloud Shell Terminal.

```
wget -q https://releases.hashicorp.com/terraform/0.13.4/terraform_0.13.4_linux_amd64.zip
unzip terraform_0.11.6_linux_amd64.zip
```

![Step 1.1: Downdloading](docs\images\terraform\1.0-download-terraform.png)

When Terraform package is uncompressed, you can move it and check its version.

```
sudo mv terraform /usr/local/bin/terraform
terraform version
```
![Step 1.2: Installing](docs\images\terraform\1.1-installed-terraform.png)

## Step 2. Configure the Service Account on GCP

In order to allow Terraform to create virtual machines, it has been created a service account which gives specific resources to a group or user.

![Step 2.10 Create Service Account](docs\images\terraform\2.0-create-account-service.png)

In *IAM & Admin* menu and then *Service accounts* it's possible to create and setting the specific roles for one service account.

For this case, it's needed to add the role *Compute Admin*.

![Step 2.1 Add role](docs\images\terraform\2.1-set-permissions.png)

Then, it's possible to create the JSON key, in this step is very important to configure ```.gitignore``` file to avoid to upload the ```credentials.json``` to the repository due to be a private key.

![Step 2.2 Select create key](docs\images\terraform\2.2-select-create-key.png)

![Step 2.3 Create json keys](docs\images\terraform\2.3-create-json-key.png)

## Step 3. Configure Terraform files
Now, its the moment when it's going to create the config files of Terraform.

### Step 3.1. ```provider.tf```

Create a file named as [```provider.tf```](provider.tf) which will contain the configuration needed for provisioning a resource on GCP.

```
# Specify the provider (GCP, AWS, Azure)
provider "google" {
	credentials = "${file("credentials.json")}"
	project = "phonic-botany-288716"
	region = "europe-west1"
}
```

### Step 3.2. ```instance.tf```

This file contains the resource's configuration of each machine that user wants to create. It has several sections:
+ ```resource "google_compute_instance" "default"```: Describe the information about the virtual machine, such as type of image, network interface or even the initial script that will going to be executed when bootstrapping.
+ ```resource "google_compute_firewall" "http-server"```: This section describes the information about the firewall or the access allowed to specific port and its protocol.

For example:

```
resource "google_compute_instance" "default" {
  name         	= "name-instance"
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
    ports    = ["80"]
  }

  // Allow traffic from everywhere to instances with an http-server tag
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]
}

output "ip" {
  value = "${google_compute_instance.default.network_interface.0.access_config.0.nat_ip}"
}
```

### Step 3.3. Create startup script

In a file like [```start.sh```](start_terraform.sh) you can define the shell commands which you want to run inside compute engine after creation. It's not mandatory but it's very interesting for example when you have to re-create instance after being deleted.

For example, it's set the commands to install *Docker*.

```
#! /bin/bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update

apt-cache policy docker-ce
sudo apt install docker-ce

sudo usermod -aG docker ${USER}
```

If it's wanted to run, for example, a *Python* command sequence instead of *Bash*, it's necessary to add to the file the following line at the start of the script: 

```
#! /usr/bin/python
```

When the instance was created, you can check that the script has been run with the [following command](https://cloud.google.com/compute/docs/startupscript#viewing_startup_script_logs):

```
sudo journalctl -u google-startup-scripts.service
```

![Check metadata startup script](docs\images\terraform\5-check-metadata-startup-script.png)

But if you don't want to use the command and see the specific file, you can read it in the following files:
 + CentOS y RHEL: ```/var/log/messages```
 + Debian: ```/var/log/daemon.log```
 + Ubuntu: ```/var/log/syslog```
 + SLES: ```/var/log/messages```

## Step 4. Resources creation

After the creation the previous files, it's ready to run a set of *Terraform* commands for resource creation.

 1. **Terraform init**: This command initializes the terraform inside a folder and creates *.terraform* directory.
 
	```
	terraform init
	```
	
	![Step 4.1. Terraform init](docs\images\terraform\3.0-terraform-init.png)

 2. **Terraform plan (optional)**: This command is used to create an execution plan. This command from 

	```
	terraform plan
	```

	![Step 4.2. Terraform plan](docs\images\terraform\3.1-terraform-plan.png)

3. **Terraform apply**: This command is used to apply the changes required to reach the desired state of the configuration, it will apply the pre-determined set of actions generated by ```terraform plan``` command.

	```
	terraform apply
	```	

	After the successful execution of these commands, we will see terraform.tfstate and terraform.tfstate.backup files in your folder. These files save the state of resources which will help update or destroy infrastructure in future. Don’t delete these files and keep it safe.

	![Step 4.3. Terraform apply](docs\images\terraform\3.2.1-terraform-apply.png)

	You have to set *yes* in order to create the specific resources.

	![Step 4.3. Terraform apply](docs\images\terraform\3.2.2-terraform-apply.png)

	Then if everything was ok, the resources are created.

	![Step 4.3. Terraform apply](docs\images\terraform\3.2.3-terraform-apply.png)

Now, you can go to your *VM Engine* console and you will see the instances which have been created by *Terraform*.

![Created instance](docs\images\terraform\4-machine-created.png)

## Useful links
+ [Create your first Compute Engine(VM) in GCP using Terraform](https://medium.com/hacker-soon/create-your-first-compute-engine-vm-in-gcp-using-terraform-3bc82f49b308)
+ [Ejecuta secuencias de comandos de inicio](https://cloud.google.com/compute/docs/startupscript#rerunthescript)
+ [HashiCorp Learn - Build Infraestructure](https://learn.hashicorp.com/tutorials/terraform/google-cloud-platform-build?in=terraform/gcp-get-started)
+ [How to Use Terraform to Create a Virtual Machine in Google Cloud Platform](https://blog.avenuecode.com/how-to-use-terraform-to-create-a-virtual-machine-in-google-cloud-platform)
+ [How to Use Terraform with Google Cloud Platform?](https://linuxhint.com/terraform_google_cloud_platform/)
+ [Terraform - google_compute_instance_template](https://www.terraform.io/docs/providers/google/r/compute_instance_template.html)