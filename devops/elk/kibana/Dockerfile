ARG ELK_STACK_VERSION

FROM docker.elastic.co/kibana/kibana:${ELK_STACK_VERSION}

COPY ./config/elasticsearch-ca.pem /usr/share/kibana/config/elasticsearch-ca.pem

COPY ./config/kibana.yml /usr/share/kibana/config/kibana.yml