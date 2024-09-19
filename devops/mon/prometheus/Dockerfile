FROM prom/prometheus:v2.52.0

COPY config/prometheus.yml /etc/prometheus/prometheus.yml
COPY config/postgres_alerts.yml /etc/prometheus/postgres_alerts.yml
# COPY config/django_alerts.yml /etc/prometheus/django_alerts.yml

EXPOSE 9090
