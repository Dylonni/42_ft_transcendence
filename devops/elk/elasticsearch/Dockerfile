ARG ELK_STACK_VERSION
ARG ELASTIC_PASSWORD


FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_STACK_VERSION}

RUN mkdir -p /usr/share/elasticsearch/config/certs
RUN ./bin/elasticsearch-certutil ca --out /usr/share/elasticsearch/config/elastic-stack-ca.p12 --pass "${ELASTIC_PASSWORD}" --silent
RUN ./bin/elasticsearch-certutil cert --ca /usr/share/elasticsearch/config/elastic-stack-ca.p12 --ca-pass "${ELASTIC_PASSWORD}" --out /usr/share/elasticsearch/config/elastic-certificates.p12  --pass "${ELASTIC_PASSWORD}" --silent
# RUN cp /usr/share/elasticsearch/config/elastic-stack-ca.p12 /usr/share/elasticsearch/config/

RUN ./bin/elasticsearch-keystore create
RUN echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.keystore.secure_password
RUN echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.truststore.secure_password



# USER root

# RUN apt-get update && \
#     apt-get install -y sudo expect && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# RUN usermod -aG sudo elasticsearch

# ARG ELASTIC_PASSWORD
# RUN echo "elasticsearch:${ELASTIC_PASSWORD}" | chpasswd

# RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config/

# USER elasticsearch


COPY ./config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
# COPY ./config/certifs.sh /usr/local/bin/certifs.sh
# RUN chmod +x /usr/local/bin/certifs.sh

# ENTRYPOINT [ "bash", "certifs.sh" ]

# COPY ./config/certifs.sh /usr/share/elasticsearch/certifs.sh
# RUN chmod +x /usr/share/elasticsearch/certifs.sh

# RUN bin/elasticsearch-reset-password -u elastic -y

# ENTRYPOINT ["/bin/bash", "/usr/share/elasticsearch/certifs.sh"]