FROM grafana/grafana:10.4.4

COPY config/grafana.ini /etc/grafana/grafana.ini

COPY provisioning/ /etc/grafana/provisioning/

COPY provisioning/dashboards/ /var/lib/grafana/dashboards/

# USER root
# COPY config/vault_token.sh /usr/local/bin/vault_token.sh
# RUN chmod +x /usr/local/bin/vault_token.sh

# ENTRYPOINT [ "/usr/local/bin/vault_token.sh" ]

EXPOSE 3000