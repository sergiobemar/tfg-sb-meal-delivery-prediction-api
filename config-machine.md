# Config REST API machine

## Step 1: Install components for the server

For this server it's used a Ubuntu machine v18.04 LTS with 2 CPUs and 4 GB of memory, besides its estimated cost is $27,31 in europe-west1 region, if machine was always on.

```
# update system packages and install the required packages
sudo apt-get update
sudo apt-get install bzip2 libxml2-dev libsm6 libxrender1 libfontconfig1 git
sudo apt-get install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install python3-venv
```
## Step 2: Set SSH keys in GitHub and clone repository

```
ssh-keygen -t rsa -b 4096 -C "youremail@email.com"

cat .ssh/id_rsa.pub
```

```
git config --global user.email "you@example.com"
git config --global user.name "Your Name"

# clone the project repo
git clone git@github.com:sergiobemar/tfg-sb-meal-delivery-prediction-api.git
```

## Step 3: Activate Python virtual environment

```
cd tfg-sb-meal-delivery-prediction-api/

python3 -m venv env

source env/bin/activate
```

## Step 4: Install libraries for the first time

```
pip install cmake wheel
pip install gunicorn flask

pip install joblib numpy pandas xgboost

```

## Step 5: Test the API

```
python serve_model.py
```

## Step 6: Configure Gunicorn

In order to keep cleaned and sorted the repository, it's changed the structure saving everything created before, all regarding to model and preprocessing scripts besides the Flask source, in a subfolder named as api.

Create a file named ```wsgi.py``` and added the following lines:
```
src api/
nano wsgi.py
```

*wsgi<span></span>.py*:
```
from app import app
if __name__ == "__main__":
    app.run(use_reloader=True, debug=True)
```

Let's run *Gunicorn*
```
gunicorn -w 3 --bind 0.0.0.0:5000 -t 30 --reload wsgi:app
```

## Step 7: Setting up the API in Docker

Create an empty ```__init__.py``` in ```api/``` and create ```requirements.txt```.

```
touch __init__.py
pip freeze > requirements.txt
```

And then, it's created ```Dockerfile``` with the following code:

```
FROM python:3.6

#update
RUN apt-get update

#install requirements
COPY ./requirements.txt /tmp/requirements.txt
WORKDIR /tmp
RUN pip3 install -r requirements.txt

#copy app
COPY . /api
WORKDIR /

CMD ["gunicorn", "-w", "3", "-bind", "0.0.0.0:5000", "-t", "360", "--reload", "api.wsgi:app"]
```

# Step 8: Add the Nginx container

```
tfg-sb-meal-delivery-prediction-api
|- api
   ...
|- nginx
	|- nginx.conf
	|- Dockerfile
```

Added the following files ```nginx.conf``` and its ```Dockerfile```. Let's see the code for the first one:

```
worker_processes  3;

events { }

http {

  keepalive_timeout  360s;

  server {

      listen 8080;
      server_name api;
      charset utf-8;

      location / {
          proxy_pass http://api:5000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      }
  }
}
```

And the ```Dockerfile``` for the nginx:

```
FROM nginx:1.15.2

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
```

# Step 9: Install Docker

To install Docker it's possible following [this tutorial](https://www.digitalocean.com/community/tutorials/como-instalar-y-usar-docker-en-ubuntu-18-04-1-es):

```
sudo apt install apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update

apt-cache policy docker-ce
sudo apt install docker-ce

sudo systemctl status docker
```

Then, current user is added to *docker* group.

```
sudo usermod -aG docker ${USER}
```

Now, you have to close the session on the server, so you can restart it or write the following command:

```
su - ${USER}
```

After that, you can check that your user is in Docker group.

```
id -nG
```

## Step 10: Install Docker Compose

It's used [docker docs web](https://docs.docker.com/compose/install/) to follow the installation steps.

```
# Get the current stable release of Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Add execution permissions to the binary
sudo chmod +x /usr/local/bin/docker-compose

# Check the version in order to test the installation
docker-compose --version
```

## Step 11: Configure Docker Compose file

```
tfg-sb-meal-delivery-prediction-api
|- api
   ...
|- nginx
   ...
|- docker-compose.yml
```

The code:

```
version: '3'

services:

  api:
    container_name: flask_api
    restart: always
    build: ./api
    volumes: ['./api:/api']
    networks:
      - apinetwork
    expose:
      - "8080"
    ports:
      - "80:8080"

  nginx:
    container_name: nginx
    restart: always
    build: ./nginx
    networks:
      - apinetwork
    expose:
      - "8787"
    ports:
      - "8787:8787"

networks:
  apinetwork:
```

## Step 12: Test docker-compose

It's the end of the configuration, if the last steps are ok, you can try to build the docker file using *docker-compose* which creates an image of the two containers, one for nginx and the other for gunicorn. When launch the command ```docker-compose up```, these containers will be up and you can try now to make some request to the API.


```
docker-compose build

docker-compose up
```

If you want to re-build the API, you only have to remove the old image and build the another newer, for this you only have to remove the created containers.

```
docker ps
docker-compose rm [IMAGE]
```
However, if you want to stop the Docker containers without being deleted, you only have to run this command from the main path:

```
docker-compose down
```