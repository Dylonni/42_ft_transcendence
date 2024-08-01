FROM grafana/grafana:10.4.4

COPY provisioning/datasources/ /etc/grafana/provisioning/datasources
COPY provisioning/dashboards/ /etc/grafana/provisioning/dashboards
# COPY provisioning/alerting/ /etc/grafana/provisioning/alerting

# dashboard for postgres
COPY provisioning/dashboards/9628_rev7.json /var/lib/grafana/dashboards/9628_rev7.json


# dashboards for django
COPY provisioning/dashboards/9528_rev1.json /var/lib/grafana/dashboards/9528_rev1.json
COPY provisioning/dashboards/17613_rev2.json /var/lib/grafana/dashboards/17613_rev2.json
COPY provisioning/dashboards/17616_rev2.json /var/lib/grafana/dashboards/17616_rev2.json
COPY provisioning/dashboards/17617_rev2.json /var/lib/grafana/dashboards/17617_rev2.json
COPY provisioning/dashboards/17658_rev2.json /var/lib/grafana/dashboards/17658_rev2.json
# COPY provisioning/dashboards/test.json /var/lib/grafana/dashboards/test.json


# COPY config/grafana.ini /etc/grafana/grafana.ini

COPY provisioning/alerting/contact_point_discord.yaml /etc/grafana/provisioning/alerting/contact_point_discord.yaml
COPY provisioning/alerting/policies-1722510964203.yaml /etc/grafana/provisioning/alerting/policies-1722510964203.yaml
# COPY provisioning/alerting/contact_point_default.yaml /etc/grafana/provisioning/alerting/contact_point_default.yaml



# COPY provisioning/alerting/alert-rules-1722511363626.yml /etc/grafana/provisioning/alerting/alert-rules-1722511363626.yml


EXPOSE 3000






