ARG ELK_STACK_VERSION

FROM docker.elastic.co/kibana/kibana:${ELK_STACK_VERSION}

RUN mkdir -p /usr/share/kibana/config

COPY ./config/kibana.yml /usr/share/kibana/config/kibana.yml

