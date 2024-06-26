# Installation Process

### Postgres_exporter will connect to our postgres database, export the metrics from it and send those to prometheus, which will be then visible in Grafana

Your ```postgres_explorer``` folder contains 1 file : <br/>
       🐋Dockerfile

## ```Dockerfile``` should contain:
    FROM prometheuscommunity/postgres-exporter:v0.14.0
    EXPOSE 9187
    [...]

## ```docker-compose.yml``` should contain:
    [...]
        postgres_exporter:
          build: ./postgres_exporter
          container_name: postgres_exporter
          env_file: .env
          ports:
            - "9187:9187"
          networks:
            - backend
    [...]

>[!CAUTION]
 >This step cannot be skipped, it will define the URL for postgres_exporter to connect to your database and do it's extraction job. Here we are using an ```.env``` file (see above) with an already configured ```DATABASE_URL``` variable so we don't have to specify an ```environment``` for our container, if you want to specify an environement in the docker-compose, you should add this instead: <br/>

      postgres_exporter:
        [...]
        environment:
          - DATABASE_URL=postgres://user:password@postgres:5432/yourdatabase?sslmode=disable
        [...]


## Modify your ```prometheus.yml``` and include:

      global:
        scrape_interval: 15s

      scrape_configs:
      
            [...]
            
        - job_name: 'postgres'
          static_configs:
            - targets:
              - postgres_exporter:9187
              labels:
                group: 'postgres-server'
    [...]
>[!NOTE]
 >Prometheus will get metrics from every source that are specified in this file <br/>

