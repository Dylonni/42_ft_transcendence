FROM owasp/modsecurity-crs:4.3.0-nginx-alpine-202406090906

USER root
RUN apk update && apk upgrade
RUN apk add --no-cache openssl

# RUN mkdir -p /etc/ssl/certs

# RUN openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

# Create OpenSSL config file for SAN
# RUN echo '[req]\n\
# default_bits = 2048\n\
# prompt = no\n\
# default_md = sha256\n\
# distinguished_name = dn\n\
# req_extensions = req_ext\n\
# \n\
# [dn]\n\
# C=FR\n\
# ST=IDF\n\
# L=Paris\n\
# O=Ecole42\n\
# OU=Stud\n\
# CN=www.transcendence42.rocks\n\
# \n\
# [req_ext]\n\
# subjectAltName = @alt_names\n\
# \n\
# [alt_names]\n\
# DNS.1 = www.transcendence42.rocks\n\
# DNS.2 = localhost\n\
# IP.1 = 127.0.0.1' > /etc/ssl/san.cnf

# RUN if [ ! -f /etc/ssl/san.cnf ]; then exit 1; fi
# COPY ./conf/cert/san.cnf /etc/ssl/san.cnf

# Generate new SSL certificate with SAN including localhost
# RUN openssl req -x509 -nodes -days 365 -sha256 -newkey rsa:2048 -keyout /etc/ssl/private/nginx_selfsigned.key -out /etc/ssl/certs/nginx_selfsigned.crt -config /etc/ssl/san.cnf -extensions req_ext


# #ssl config
# RUN openssl req -x509 -nodes -days 365 -sha256 -newkey rsa:2048 -keyout /etc/ssl/private/nginx_selfsigned.key  -out /etc/ssl/certs/nginx_selfsigned.crt -subj "/C=FR/ST=IDF/L=Paris/O=Ecole42/OU=Stud/CN=ft_transcendence"
# RUN openssl req -x509 -new -newkey rsa:2048 -nodes -days 365 -sha256 -out /etc/ssl/certs/www_transcendence42_rocks.csr -keyout /etc/ssl/private/www_transcendence42_rocks.key -subj "/C=FR/ST=Ile-de-France/L=Paris/O=Ecole42/CN=www.transcendence42.rocks"
# COPY ./conf/trans_cert.pem /etc/ssl/certs/nginx.crt
# COPY ./conf/trans_key.pem /etc/ssl/private/nginx.key


# should : copy all .crt, then cat cert ca_bundle >> cert (and not in a new file, as checksum would not match)
# COPY ./conf/cert/ca_bundle.crt /etc/ssl/ca_bundle.crt
# COPY ./conf/cert/certificate.crt /etc/ssl/certificate.crt
# COPY ./conf/cert/private.key /etc/ssl/private.key


COPY ./conf/vault.conf /etc/nginx/conf.d/vault.conf
COPY ./conf/postgres-exporter.conf /etc/nginx/conf.d/postgres-exporter.conf
COPY ./conf/prometheus.conf /etc/nginx/conf.d/prometheus.conf
COPY ./conf/grafana.conf /etc/nginx/conf.d/grafana.conf
COPY ./conf/elasticsearch.conf /etc/nginx/conf.d/elasticsearch.conf
COPY ./conf/logstash.conf /etc/nginx/conf.d/logstash.conf
COPY ./conf/kibana.conf /etc/nginx/conf.d/kibana.conf

COPY ./conf/nginx.conf /etc/nginx/templates/conf.d/default.conf.template
COPY ./conf/modsecurity.conf /etc/nginx/templates/modsecurity.d/modsecurity.conf.template

COPY ./conf/proxy_backend.conf /etc/nginx/conf.d/proxy_backend.conf

# RUN sudo chmod -R 755 /usr/share/nginx/html
# RUN sudo chown -R www-data:www-data /usr/share/nginx/html

EXPOSE 8080 8443