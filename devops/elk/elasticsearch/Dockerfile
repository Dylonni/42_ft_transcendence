ARG ELK_STACK_VERSION
ARG ELASTIC_PASSWORD


FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_STACK_VERSION}



USER root

RUN apt-get update && \
    apt-get install -y expect && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY ./config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml


COPY ./config/certutils_http.sh /usr/share/elasticsearch/certutils_http.sh
RUN chmod +x /usr/share/elasticsearch/certutils_http.sh

COPY ./config/utils.sh /usr/share/elasticsearch/utils.sh
RUN chmod +x /usr/share/elasticsearch/utils.sh


COPY ./config/startup.sh /usr/share/elasticsearch/startup.sh
RUN chmod +x /usr/share/elasticsearch/startup.sh

# USER elasticsearch


# ENTRYPOINT ["/usr/share/elasticsearch/startup.sh"]
CMD ["/bin/bash", "-c", "/usr/share/elasticsearch/startup.sh"]

