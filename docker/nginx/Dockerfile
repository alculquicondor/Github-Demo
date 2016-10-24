FROM nginx
MAINTAINER Aldo Culquicondor "alculquicondor@gmail.com"

RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx/all.conf /etc/nginx/conf.d/all.conf

COPY static /srv/gis
