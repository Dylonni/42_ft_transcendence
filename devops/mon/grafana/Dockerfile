FROM grafana/grafana:10.4.4

COPY provisioning/datasources/ /etc/grafana/provisioning/datasources
COPY provisioning/dashboards/ /etc/grafana/provisioning/dashboards
COPY provisioning/dashboards/9628_rev7.json /var/lib/grafana/dashboards/9628_rev7.json




# COPY provisioning/dashboards/7996_rev3.json /var/lib/grafana/dashboards/7996_rev3.json
COPY provisioning/dashboards/9528_rev1.json /var/lib/grafana/dashboards/9528_rev1.json
COPY provisioning/dashboards/17613_rev2.json /var/lib/grafana/dashboards/17613_rev2.json
COPY provisioning/dashboards/17616_rev2.json /var/lib/grafana/dashboards/17616_rev2.json
COPY provisioning/dashboards/17617_rev2.json /var/lib/grafana/dashboards/17617_rev2.json
COPY provisioning/dashboards/17658_rev2.json /var/lib/grafana/dashboards/17658_rev2.json


EXPOSE 3000



# tools to create django dashboards
# https://github.com/adinhodovic/django-mixin
# https://github.com/korfuri/django-prometheus