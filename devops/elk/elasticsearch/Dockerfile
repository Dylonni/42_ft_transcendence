ARG ELK_STACK_VERSION

# FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_STACK_VERSION}

FROM docker.elastic.co/elasticsearch/elasticsearch:8.14.1


USER root

# RUN apt-get update && \
#     apt-get install -y expect && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# ARG ELASTIC_PASSWORD


# COPY ./config/e5-cross.pem /etc/ssl/certs/e5-cross.pem
# COPY ./config/e6-cross.pem /etc/ssl/certs/e6-cross.pem
# COPY ./config/trans_cert.pem /etc/ssl/certs/trans_cert.pem
# COPY ./config/trans_key.pem /etc/ssl/certs/trans_key.pem
# COPY ./config/elasticsearch.p12 /usr/share/elasticsearch/config/elasticsearch.p12




# RUN cat /etc/ssl/certs/trans_cert.pem /etc/ssl/certs/e5-cross.pem /etc/ssl/certs/e6-cross.pem > /etc/ssl/certs/fullchain.pem

# RUN chmod +x /etc/ssl/certs/trans_key.pem

# RUN openssl pkcs12 -export -out /usr/share/elasticsearch/config/elasticsearch.p12 -inkey /etc/ssl/certs/trans_key.pem -in /etc/ssl/certs/fullchain.pem -name "elasticsearch" -passout pass:${ELASTIC_PASSWORD}


# RUN chown elasticsearch:elasticsearch /usr/share/elasticsearch/config/elasticsearch.p12
# RUN chmod 600 /usr/share/elasticsearch/config/elasticsearch.p12

RUN chown elasticsearch:elasticsearch /usr/share/elasticsearch/bin/elasticsearch-keystore

USER elasticsearch

# RUN export ; exit 1

RUN ./bin/elasticsearch-keystore create
# RUN echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.keystore.secure_password
# RUN echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.truststore.secure_password

# USER elasticsearch

# RUN openssl pkcs12 -info -in /usr/share/elasticsearch/config/elasticsearch.p12 -passin pass:${ELASTIC_PASSWORD}
COPY ./config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml

RUN echo "Listing keystore permissions:" && ls -l /usr/share/elasticsearch/bin/elasticsearch-keystore
RUN echo "Current user:" && whoami

# ENTRYPOINT ["/usr/share/elasticsearch/startup.sh"]
# CMD ["/bin/bash", "-c", "/usr/share/elasticsearch/startup.sh"]

