# Installation Process

Your elasticsearch folder should contain 1 folder and 2 files : <br/>
        📂config<br/>
       └ elasticsearch.yml<br/>   🐋Dockerfile

# ```Dockerfile``` should contain:
      ARG ELK_STACK_VERSION
      FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_STACK_VERSION}
      COPY ./config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
    [...]

# ```docker-compose.yml``` should contain:
    [...] 
       elasticsearch:
         build:
           context: ./elasticsearch
           args:
             ELK_STACK_VERSION: ${ELK_STACK_VERSION}
         container_name: elasticsearch
         environment:
           node.name: elasticsearch
           discovery.type: single-node
           ES_JAVA_OPTS: -Xms512m -Xmx512m
           ELASTIC_PASSWORD: ${ELASTIC_PASSWORD:-}
         networks:
           - backend
           - elk
         ports:
           - "9200:9200"
    [...]

# Modify your ```elasticsearch.yml``` and include :

      cluster.name: docker-cluster
      network.host: 0.0.0.0

      xpack.license.self_generated.type: trial
      xpack.security.enabled: false

    [...]
