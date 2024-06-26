# Installation Process

Your ```grafana``` folder tree should looke like this : <br/>
       📂provisioning<br/>
        └ 📂dashboards<br/>
    └ your_dashboard.json<br/>
    └ dashboard.yml<br/>
        └📂datasources<br/>
    └ datasources.yml<br/>
       🐋Dockerfile
## ```dashboard.yml``` should contain:
      apiVersion: 1
      providers:
        - name: 'Postgres Dashboard'
          orgId: 1
          folder: ''
          type: file
          disableDeletion: true
          updateIntervalSeconds: 10
          options:
            path: /var/lib/grafana/dashboards
## ```datasources.yml``` should contain:
      apiVersion: 1
      datasources:
        - name: Prometheus
          type: prometheus
          access: proxy
          url: http://prometheus:9090
          isDefault: true
          editable: true
>[!NOTE]
 >These are default configuration for provisioning Grafana that can be found here: https://grafana.com/docs/grafana/latest/administration/provisioning/.
 >We want to import our own dashboards to Grafana, so we specify a path of where to find them. Note that we also are specifying our datasource to be ```prometheus``` since we want to get all of our metrics from there.
 >The file ```your_dashboard.json``` is a file that you can either export from [Grafana](https://grafana.com/grafana/dashboards/) or that you can build yourself. You can also put more dashboards in the```📂dashboards``` folder.

## ```Dockerfile``` should contain:
    FROM grafana/grafana:10.4.4-ubuntu
    EXPOSE 3000
    [...]

## ```docker-compose.yml``` should contain:
    [...]
        grafana:
          build: ./grafana
          container_name: grafana
          env_file:
            - .env
          depends_on:
            - prometheus
          networks:
            - backend
          ports:
            - "3000:3000"
          volumes:
            - ./grafana/provisioning/datasources/:/etc/grafana/provisioning/datasources
            - ./grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards
            - ./grafana/provisioning/dashboards/your_dashboard.json:/var/lib/grafana/dashboards/your_dashboard.json
    [...]

>[!NOTE]
 >By default, Grafana credentials are admin/admin. 
The user is prompted to change password upon his first time connecting to Grafana.
You can change those credentials early on and not be prompted by modifying these environment variables which for us are located in the ```.env``` file <br/>

    GF_SECURITY_ADMIN_USER
    GF_SECURITY_ADMIN_PASSWORD

# Accessing GUI

>[!NOTE]
 >Grafana can take some time to be up and running, it's normal if you can't access it fast nor if your dashboards doesn't show metrics right away. it should be fine after some wait<br/>

Once your containers are running , you can acces your metrics via Grafana's interface by connecting to ```localhost:3000``` and entering your credentials.
