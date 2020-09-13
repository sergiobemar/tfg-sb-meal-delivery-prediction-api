# Meal Delivery Prediction - API

Repository to launch, deploy and maintain the API for the TFG project "Meal Delivery Prediction" used for showing the user every metrics and KPIs about the activity of the different center in their activity, delivery several meals. 

This API send the response from the requests sent by the[ ShinyApp deployed for this use case](https://github.com/sergiobemar/tfg-sb-meal-delivery-prediction), where the user can make several predictions about the number of orders which are estimated for the next 10 weeks.

## Anatomy

```
.
├── README.md				-The top-level README for developers using this project
├── .gitignore				- File containing folders & files to be ignored in the GIT repository (e.g. everything in data, models and reports folders)
├── api					- Folder with the code regarding the API server
│   ├── Dockerfile			- File used by Docker to generate the image of the API server launched by Gunicorn
│   ├── __init__.py			- Makes api a Python module
│   ├── app.py				- Script with Flask code to lauch manage the requests to the several endpoints
│   ├── data				- Files with the different datasets
│   │   ├── processed			- Processed datasets
│   │   └── raw				- Original datasets
│   ├── endpoints			- Scripts with the different endpoints that it's wanted to expose by the server
│   ├── models				- To save the models in binary format
│   ├── notebooks			- Used in order to explore both data and the different functionalities
│   ├── references			- Some files with links or relevant information for the notebooks
│   ├── reports				- Reports generated by notebooks, not in .ipynb or .Rmd formats
│   ├── requirements.txt		- The requirements file for reproducing the analysis environment, e.g. generated with `pip freeze > requirements.txt`
│   ├── src				- Source code for use in this project
│   │   ├── __init__.py			- Makes src a Python module
│   │   ├── data			- Scripts to download or generate data
│   │   ├── deploy			- Scripts to turn raw data into features for modeling
│   │   ├── model			- Scripts to train models and then use trained models to make predictions
│   │   └── test			- Scripts or config files to test some functionalities before implementing in the application
│   └── wsgi.py				- Used by Gunicorn to start app.py
├── docker-compose.yml			- Manage our Docker containers assembling them
├── config-machine.md			- Guide for developers to deploy this repository
└── nginx				- Scripts related to Nginx configuration
    ├── Dockerfile			- File used by Docker to generate the image of the Nginx 
    └── nginx.conf			- Configure the web server
```



## How to run

# Useful links
+ A production-grade Machine Learning API using Flask, Gunicorn, Nginx, and Docker
 + [Part 1: Setting up our API](https://medium.com/technonerds/a-production-grade-machine-learning-api-using-flask-gunicorn-nginx-and-docker-part-1-49927238befb)
 + [Part 2: Integrating Gunicorn, Nginx and Docker](https://medium.com/technonerds/a-production-grade-machine-learning-api-using-flask-gunicorn-nginx-and-docker-part-2-c69629199037)
 + [Part 3: Flask Blueprints — managing multiple endpoints](https://medium.com/technonerds/a-production-grade-machine-learning-api-using-flask-gunicorn-nginx-and-docker-part-3-flask-30c881a65655)
 + [Part 4: Testing your ML API](https://medium.com/technonerds/a-production-grade-machine-learning-api-using-flask-gunicorn-nginx-and-docker-part-4-unit-c31a92544fd6)
+ [Cómo instalar y usar Docker en Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/como-instalar-y-usar-docker-en-ubuntu-18-04-1-es)
+ [Cómo preparar aplicaciones de Flask con Gunicorn y Nginx en Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/como-preparar-aplicaciones-de-flask-con-gunicorn-y-nginx-en-ubuntu-18-04-es)
+ [Deploying an ML Model on Google Compute Engine](https://towardsdatascience.com/deploying-a-custom-ml-prediction-service-on-google-cloud-ae3be7e6d38f)
+ [Install Docker Compose](https://docs.docker.com/compose/install/)
+ [Where Are Docker Container Logs Stored?](https://sematext.com/blog/docker-logs-location/#:~:text=First%20of%20all%2C%20to%20list,use%20the%20docker%20ps%20command.&text=Then%2C%20with%20the%20docker%20logs,logs%20for%20a%20particular%20container.&text=Most%20of%20the%20time%20you,the%20last%20few%20logs%20lines.)