FROM prom/alertmanager:v0.27.0

RUN mkdir -p /etc/alertmanager

COPY config/alertmanager.yml /etc/alertmanager/alertmanager.yml

EXPOSE 9093
