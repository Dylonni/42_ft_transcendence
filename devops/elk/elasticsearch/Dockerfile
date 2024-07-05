ARG ELK_STACK_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_STACK_VERSION}


# USER root

COPY ./config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
# COPY ./config/certifs.sh /usr/local/bin/certifs.sh
# RUN chmod +x /usr/local/bin/certifs.sh

# ENTRYPOINT [ "bash", "certifs.sh" ]

COPY ./config/certifs.sh /usr/share/elasticsearch/certifs.sh
# RUN chmod +x /usr/share/elasticsearch/certifs.sh


ENTRYPOINT ["/bin/bash", "/usr/share/elasticsearch/certifs.sh"]