FROM owasp/modsecurity-crs:4.3.0-nginx-alpine-202406090906

USER root
RUN apk update && apk upgrade
RUN apk add --no-cache openssl

# #ssl config

# RUN openssl req -x509 -nodes -days 365 -sha256 -newkey rsa:2048 -keyout /etc/ssl/private/nginx_selfsigned.key  -out /etc/ssl/certs/nginx_selfsigned.crt -subj "/C=FR/ST=IDF/L=Paris/O=Ecole42/OU=Stud/CN=ft_transcendence"
RUN openssl req -x509 -new -newkey rsa:2048 -nodes -days 365 -sha256 -out /etc/ssl/certs/www_transcendence42_rocks.csr -keyout /etc/ssl/private/www_transcendence42_rocks.key -subj "/C=FR/ST=Ile-de-France/L=Paris/O=Ecole42/CN=www.transcendence42.rocks"


COPY ./conf/vault.conf /etc/nginx/conf.d/vault.conf
COPY ./conf/postgres-exporter.conf /etc/nginx/conf.d/postgres-exporter.conf
COPY ./conf/prometheus.conf /etc/nginx/conf.d/prometheus.conf
COPY ./conf/grafana.conf /etc/nginx/conf.d/grafana.conf
COPY ./conf/elasticsearch.conf /etc/nginx/conf.d/elasticsearch.conf
COPY ./conf/logstash.conf /etc/nginx/conf.d/logstash.conf
COPY ./conf/kibana.conf /etc/nginx/conf.d/kibana.conf
COPY ./conf/nginx.conf /etc/nginx/templates/conf.d/default.conf.template


EXPOSE 8080 8443