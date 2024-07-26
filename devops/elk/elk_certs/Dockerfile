ARG ELK_STACK_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_STACK_VERSION}


# RUN mkdir -p /usr/share/elasticsearch/config/certs 

USER root
RUN mkdir -p /usr/share/elasticsearch/config/certs && \
	chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config/certs


COPY ./config/cert.yml /usr/share/elasticsearch/config/certs/cert.yml

COPY ./config/init.sh /usr/share/elasticsearch/init.sh
RUN chmod +x /usr/share/elasticsearch/init.sh

# RUN bin/elasticsearch-certutil ca --silent --pem -out config/certs/ca.zip; unzip config/certs/ca.zip -d config/certs;

# RUN bin/elasticsearch-certutil cert --silent --pem --in config/certs/ca.zip --out config/certs/cert.zip; unzip config/certs/cert.zip -d config/certs;

# RUN mkdir -p /usr/share/elasticsearch/config/certs && \
#     /usr/share/elasticsearch/bin/elasticsearch-certutil ca --silent --pem --pass "${ELASTIC_PASSWORD}" -out /usr/share/elasticsearch/config/certs/ca.zip && \
#     unzip /usr/share/elasticsearch/config/certs/ca.zip -d /usr/share/elasticsearch/config/certs && \
#     rm /usr/share/elasticsearch/config/certs/ca.zip && \
#     /usr/share/elasticsearch/bin/elasticsearch-certutil cert --silent --pem --ca /usr/share/elasticsearch/config/certs/ca/ca.crt --ca-pass "${ELASTIC_PASSWORD}" --out /usr/share/elasticsearch/config/certs/cert.zip && \
#     unzip /usr/share/elasticsearch/config/certs/cert.zip -d /usr/share/elasticsearch/config/certs && \
#     rm /usr/share/elasticsearch/config/certs/cert.zip



# RUN chown -R root:root config/certs; find . -type d -exec chmod 750 \{\} \; find . -type f -exec chmod 640 \{\} \;


# RUN until curl -s --cacert /usr/share/elasticsearch/config/certs/ca/ca.crt https://elasticsearch:9200 | grep -q "missing authentication credentials"; do sleep 30; done;
# RUN until curl -s -X POST --cacert /usr/share/elasticsearch/config/certs/ca/ca.crt -u "elastic:${ELASTIC_PASSWORD}" -H "Content-Type: application/json" https://elasticsearch:9200/_security/user/kibana_system/_password -d "{\"password\":\"${KIBANA_PASSWORD}\"}" | grep -q "^{}"; do sleep 10; done;


# USER elasticsearch



ENTRYPOINT [ "/usr/share/elasticsearch/init.sh" ]