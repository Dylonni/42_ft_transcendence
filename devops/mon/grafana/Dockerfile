FROM grafana/grafana:10.4.4

## remove ?
# COPY grafana.ini /etc/grafana/grafana.ini


COPY provisioning/datasources/ /etc/grafana/provisioning/datasources
COPY provisioning/dashboards/ /etc/grafana/provisioning/dashboards
COPY provisioning/alerting/ /etc/grafana/provisioning/alerting


COPY provisioning/dashboards/ /var/lib/grafana/dashboards/



EXPOSE 3000