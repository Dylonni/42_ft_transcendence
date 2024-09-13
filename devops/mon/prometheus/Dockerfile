FROM prom/prometheus:v2.52.0

COPY config/prometheus.yml /etc/prometheus/prometheus.yml
COPY config/postgres_alerts.yml /etc/prometheus/postgres_alerts.yml

EXPOSE 9090
