FROM python:3.6

#update
RUN apt-get update 
# && apt-get install -y python3-dev
# RUN apt-get -y install pkg-config libsystemd-journal-dev

#install requirements
COPY ./requirements.txt /tmp/requirements.txt
WORKDIR /tmp
#RUN pip3 install requests
#RUN apt-get -y install python3-requests
RUN pip3 install -r requirements.txt

#copy app
COPY . /api
WORKDIR /

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "-t", "360", "--reload", "api.app:app", "-k", "uvicorn.workers.UvicornWorker"]
