ARG ELK_STACK_VERSION

FROM docker.elastic.co/kibana/kibana:${ELK_STACK_VERSION}

USER root

RUN mkdir -p /usr/share/kibana/config

COPY ./config/kibana.yml /usr/share/kibana/config/kibana.yml

COPY ./config/kib_wait.sh /usr/share/kibana/kib_wait.sh
RUN chmod +x /usr/share/kib_wait.sh

USER kibana

ENTRYPOINT [ "/usr/share/kibana/kib_wait.sh" ]

