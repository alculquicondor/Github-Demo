FROM python:3
MAINTAINER Aldo Culquicondor "alculquicondor@gmail.com"

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /srv/gis
COPY app/ ./

# CMD gunicorn -b 0.0.0.0:8000 -w 2 gis:app
