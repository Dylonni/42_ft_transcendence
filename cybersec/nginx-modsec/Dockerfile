FROM owasp/modsecurity-crs:4.3.0-nginx-alpine-202406090906

USER root
RUN apk update && apk upgrade
RUN apk add --no-cache openssl



# ssl only for website
# COPY ./conf/vault.conf /etc/nginx/conf.d/vault.conf
# COPY ./conf/postgres-exporter.conf /etc/nginx/conf.d/postgres-exporter.conf
# COPY ./conf/prometheus.conf /etc/nginx/conf.d/prometheus.conf
# COPY ./conf/elasticsearch.conf /etc/nginx/conf.d/elasticsearch.conf
# COPY ./conf/logstash.conf /etc/nginx/conf.d/logstash.conf
# COPY ./conf/kibana.conf /etc/nginx/conf.d/kibana.conf
# COPY ./conf/loki.conf /etc/nginx/conf.d/loki.conf
# COPY ./conf/redis.conf /etc/nginx/conf.d/redis.conf
# COPY ./conf/proxy_backend.conf /etc/nginx/conf.d/proxy_backend.conf
# COPY ./conf/grafana.conf /etc/nginx/conf.d/grafana.conf
# COPY ./conf/old_nginx.conf /etc/nginx/templates/conf.d/default.conf.template

# COPY ./conf/modsecurity.conf /etc/nginx/templates/modsecurity.d/modsecurity-override.conf.template






# ssl for all
COPY ./conf/testnginx.conf /etc/nginx/templates/conf.d/default.conf.template
## ADD MODSEC !!




EXPOSE 8080 8443