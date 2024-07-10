ARG ELK_STACK_VERSION
ARG ELASTIC_PASSWORD


FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_STACK_VERSION}

# ENV ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
# # ENV ELASTIC_PASSWORD=elastic
# RUN if [ -z "$ELASTIC_PASSWORD" ]; then echo "ELASTIC_PASSWORD is not set" && exit 1; else echo "ELASTIC_PASSWORD is set to '$ELASTIC_PASSWORD'"; fi


# RUN mkdir -p /usr/share/elasticsearch/config/certs
# RUN ./bin/elasticsearch-certutil ca --out /usr/share/elasticsearch/config/elastic-stack-ca.p12 --pass "${ELASTIC_PASSWORD}" --silent
# RUN ./bin/elasticsearch-certutil cert --ca /usr/share/elasticsearch/config/elastic-stack-ca.p12 --ca-pass "${ELASTIC_PASSWORD}" --out /usr/share/elasticsearch/config/elastic-certificates.p12  --pass "${ELASTIC_PASSWORD}" --silent
# RUN cp /usr/share/elasticsearch/config/elastic-stack-ca.p12 /usr/share/elasticsearch/config/

RUN ./bin/elasticsearch-keystore create
RUN echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.keystore.secure_password
RUN echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.truststore.secure_password



COPY ./config/elastic-certificates.p12 /usr/share/elasticsearch/elastic-certificates.p12
COPY ./config/elasticsearch.crt /usr/share/elasticsearch/elasticsearch.crt
COPY ./config/elasticsearch.key /usr/share/elasticsearch/elasticsearch.key
COPY ./config/elasticsearch.p12 /usr/share/elasticsearch/elasticsearch.p12
COPY ./config/elastic-stack-ca.p12 /usr/share/elasticsearch/elastic-stack-ca.p12


# COPY ./config/elasticsearch.keystore /usr/share/elasticsearch/config/elasticsearch.keystore
COPY ./config/http.p12 /usr/share/elasticsearch/config/http.p12

RUN mkdir -p /usr/share/elasticsearch/kibana-server
COPY ./config/kibana-server.csr /usr/share/elasticsearch/kibana-server/kibana-server.csr
COPY ./config/kibana-server.key /usr/share/elasticsearch/kibana-server/kibana-server.key





RUN echo ${ELASTIC_PASSWORD} | ./bin/elasticsearch-keystore add --stdin xpack.security.http.ssl.keystore.secure_password

# USER root
# ENV ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
# RUN apt-get update && \
#     apt-get install -y sudo expect && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# RUN usermod -aG sudo elasticsearch

# RUN echo "elasticsearch:${ELASTIC_PASSWORD}" | chpasswd

# RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config/

# COPY ./config/certutils_http.sh /usr/share/elasticsearch/certutils_http.sh
# RUN chmod +x /usr/share/elasticsearch/certutils_http.sh


# COPY ./config/cert2.sh /usr/share/elasticsearch/cert2.sh
# RUN chmod +x /usr/share/elasticsearch/cert2.sh

# COPY ./config/exp2.sh /usr/share/elasticsearch/exp2.sh
# RUN chmod +x /usr/share/elasticsearch/exp2.sh

# COPY ./config/script.exp /usr/share/elasticsearch/script.exp
# RUN chmod +x /usr/share/elasticsearch/script.exp

# RUN if [ -z "$ELASTIC_PASSWORD" ]; then echo "ELASTIC_PASSWORD is not set" && exit 1; else echo "ELASTIC_PASSWORD is set to '$ELASTIC_PASSWORD'"; fi
# RUN /usr/share/elasticsearch/certutils.sh

# USER elasticsearch

# RUN echo "" | ./bin/elasticsearch-keystore add --stdin xpack.security.http.ssl.keystore.secure_password


# COPY ./config/http.p12 /usr/share/elasticsearch/config/http.p12
# COPY ./config/cert.yml /usr/share/elasticsearch/config/cert.yml
# RUN bin/elasticsearch-certutil http --batch --config /usr/share/elasticsearch/config/cert.yml -out /usr/share/elasticsearch/elasticsearch-ssl-http.zip
# RUN bin/elasticsearch-certutil http /usr/share/elasticsearch/config/cert.yml -v
# RUN echo "${ELASTIC_PASSWORD}" | bin/elasticsearch-certutil http --in config/cert.yml -out elasticsearch-ssl-http.zip --days 90 --ca /usr/share/elasticsearch/config/elastic-stack-ca.p12 --ca-pass "${ELASTIC_PASSWORD}"

# RUN unzip /usr/share/elasticsearch/elasticsearch-ssl-http.zip -d /usr/share/elasticsearch/

# RUN cp /usr/share/elasticsearch/elasticsearch-ssl-http/elasticsearch/http.p12 /usr/share/elasticsearch/config/http.p12

# RUN ./bin/elasticsearch-certutil http --silent --in /usr/share/elasticsearch/config/certs.yml \
#     && echo "Setting up keystore" \
#     && (echo "your_keystore_password"; echo "your_keystore_password") | ./bin/elasticsearch-keystore add xpack.security.http.ssl.keystore.secure_password


COPY ./config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
# COPY ./config/certifs.sh /usr/local/bin/certifs.sh
# RUN chmod +x /usr/local/bin/certifs.sh

# ENTRYPOINT [ "bash", "certifs.sh" ]

# COPY ./config/certifs.sh /usr/share/elasticsearch/certifs.sh
# RUN chmod +x /usr/share/elasticsearch/certifs.sh

# RUN bin/elasticsearch-reset-password -u elastic -y

COPY ./config/fullscript.sh /usr/share/elasticsearch/fullscript.sh
# RUN chmod +x /usr/share/elasticsearch/fullscript.sh


# ENTRYPOINT ["/usr/share/elasticsearch/certutils_http.sh"]
# ENTRYPOINT ["/usr/share/elasticsearch/fullscript.sh"]

# ENTRYPOINT /usr/share/elasticsearch/script.exp