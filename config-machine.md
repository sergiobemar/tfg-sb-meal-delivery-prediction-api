# Configurate machine

## Step 1: Install components for the server
```
# update system packages and install the required packages
sudo apt-get update
sudo apt-get install bzip2 libxml2-dev libsm6 libxrender1 libfontconfig1
sudo apt-get install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install python3-venv
```
# Step 2. Set SSH keys in GitHub and clone repository

```
ssh-keygen -t rsa -b 4096 -C "youremail@email.com"

cat .ssh/id_rsa.pub
```

```
# clone the project repo
git clone git@github.com:sergiobemar/tfg-sb-meal-delivery-prediction-api.git
```

## Step 3: Activate Python virtual environment
```
cd tfg-sb-meal-delivery-prediction-api/

python3 -m venv env

source env/bin/activate
```
# Step 4: Install libraries for the first time

```
pip install cmake wheel
pip install gunicorn flask

pip install joblib numpy pandas xgboost

```


```
sudo apt-get install python3-pip

# download and install miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-4.7.10-Linux-x86_64.sh
bash Miniconda3-4.7.10-Linux-x86_64.sh
```

```
export PATH=/home/<your name here>/miniconda3/bin:$PATH
rm Miniconda3-4.7.10-Linux-x86_64.sh

# confirm installation
which conda

# create and activate a new environment
conda create -n flask-tutorial python=3.7
conda activate flask-tutorial
```












