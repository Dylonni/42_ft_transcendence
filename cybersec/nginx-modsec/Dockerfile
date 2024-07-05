FROM owasp/modsecurity-crs:4.3.0-nginx-alpine-202406090906

COPY ./conf/vault.conf /etc/nginx/conf.d/vault.conf
COPY ./conf/postgres-exporter.conf /etc/nginx/conf.d/postgres-exporter.conf
COPY ./conf/prometheus.conf /etc/nginx/conf.d/prometheus.conf
COPY ./conf/grafana.conf /etc/nginx/conf.d/grafana.conf
COPY ./conf/elasticsearch.conf /etc/nginx/conf.d/elasticsearch.conf
COPY ./conf/logstash.conf /etc/nginx/conf.d/logstash.conf
COPY ./conf/kibana.conf /etc/nginx/conf.d/kibana.conf

EXPOSE 8080 8443