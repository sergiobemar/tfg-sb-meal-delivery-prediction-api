FROM python:3.6

#update
RUN apt-get update 

#install requirements
COPY ./api/requirements.txt /tmp/requirements.txt
WORKDIR /tmp
RUN pip3 install -r requirements.txt

#copy app
COPY api /api
WORKDIR /

COPY .credentials /.credentials

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "-t", "360", "--reload", "api.app:app", "-k", "uvicorn.workers.UvicornWorker"]
