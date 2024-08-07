FROM grafana/grafana:10.4.4

COPY provisioning/datasources/ /etc/grafana/provisioning/datasources
COPY provisioning/dashboards/ /etc/grafana/provisioning/dashboards
COPY provisioning/alerting/ /etc/grafana/provisioning/alerting

# dashboard for postgres
COPY provisioning/dashboards/9628_rev7.json /var/lib/grafana/dashboards/9628_rev7.json



# # dashboards for django
COPY provisioning/dashboards/9528_rev1.json /var/lib/grafana/dashboards/9528_rev1.json
COPY provisioning/dashboards/17613_rev2.json /var/lib/grafana/dashboards/17613_rev2.json
COPY provisioning/dashboards/17616_rev2.json /var/lib/grafana/dashboards/17616_rev2.json
COPY provisioning/dashboards/17617_rev2.json /var/lib/grafana/dashboards/17617_rev2.json
COPY provisioning/dashboards/17658_rev2.json /var/lib/grafana/dashboards/17658_rev2.json


# COPY provisioning/alerting/contact_point_discord.yaml /var/lib/grafana/alerting/contact_point_discord.yaml
# COPY provisioning/alerting/contact_point_default.yaml /var/lib/grafana/alerting/contact_point_default.yaml
# COPY provisioning/alerting/policies-1722510964203.yaml /var/lib/grafana/alerting/policies-1722510964203.yaml




EXPOSE 3000



# tools to create django dashboards
# https://github.com/adinhodovic/django-mixin
# https://github.com/korfuri/django-prometheus