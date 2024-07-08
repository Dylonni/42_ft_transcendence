ARG ELK_STACK_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_STACK_VERSION}


USER root
# RUN apt-get update && apt-get upgrade
# RUN apt-get install -y sudo

# RUN sudo useradd elastic -p elastic

RUN apt-get update && \
    apt-get install -y sudo expect && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# RUN apt-get install -y expect

RUN usermod -aG sudo elasticsearch

ARG ELASTIC_PASSWORD
RUN echo "elasticsearch:${ELASTIC_PASSWORD}" | chpasswd

RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config/

USER elasticsearch
# RUN echo elastic:elastic | chpasswd

COPY ./config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
# COPY ./config/certifs.sh /usr/local/bin/certifs.sh
# RUN chmod +x /usr/local/bin/certifs.sh

# ENTRYPOINT [ "bash", "certifs.sh" ]

COPY ./config/certifs.sh /usr/share/elasticsearch/certifs.sh
# RUN chmod +x /usr/share/elasticsearch/certifs.sh

# RUN bin/elasticsearch-reset-password -u elastic -y

ENTRYPOINT ["/bin/bash", "/usr/share/elasticsearch/certifs.sh"]