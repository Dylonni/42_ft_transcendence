
# Installation Process

Your ```kibana``` folder should contain 1 folder and 2 files : <br/>
        📂config<br/>
       └ kibana.yml<br/>   
       🐋Dockerfile

## ```Dockerfile``` should contain:
    ARG ELK_STACK_VERSION
    FROM docker.elastic.co/kibana/kibana:${ELK_STACK_VERSION}
    COPY ./config/kibana.yml /usr/share/kibana/config/kibana.yml
    [...]

## ```docker-compose.yml``` should contain:
    [...] 
    kibana:
      build:
        context: ./kibana
        args:
          ELK_STACK_VERSION: ${ELK_STACK_VERSION}
      container_name: kibana
      environment:
        KIBANA_SYSTEM_PASSWORD: ${KIBANA_SYSTEM_PASSWORD:-}
      depends_on:
        - elasticsearch
      networks:
        - backend
        - elk
      ports:
        - "5601:5601"
    [...]

## Modify your ```elasticsearch.yml``` and include :

    server.name: kibana
    server.host: 0.0.0.0
    elasticsearch.hosts: [ http://elasticsearch:9200 ]

    monitoring.ui.container.elasticsearch.enabled: true
    monitoring.ui.container.logstash.enabled: true

    elasticsearch.username: kibana_system
    elasticsearch.password: ${KIBANA_SYSTEM_PASSWORD}
    [...]
