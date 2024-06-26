ARG ELK_STACK_VERSION

FROM docker.elastic.co/logstash/logstash:${ELK_STACK_VERSION}

COPY ./pipeline/logstash.conf /usr/share/logstash/pipeline/logstash.conf
