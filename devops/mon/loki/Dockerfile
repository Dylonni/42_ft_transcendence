FROM grafana/loki:2.9.10


COPY config/local-config.yaml /etc/loki/local-config.yaml

CMD ["-config.file=/etc/loki/local-config.yaml"]

EXPOSE 3100


# Verify that Loki is up and running.
#     To view readiness, navigate to http://localhost:3100/ready.
#     To view metrics, navigate to http://localhost:3100/metrics.