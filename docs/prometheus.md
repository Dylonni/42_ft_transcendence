# Installation Process

Your ```prometheus``` folder should contain 2 files : <br/>
  🐋Dockerfile <br/>
   prometheus.yml <br/>

Install ```django-prometheus``` into your django app, here we use pipenv <br/>
 ```$ pipenv install django-prometheus ```

## ```Dockerfile``` should contain:
    FROM prom/prometheus:v2.52.0
    COPY prometheus.yml /etc/prometheus/prometheus.yml
    EXPOSE 9090
    [...]

## ```docker-compose.yml``` should contain:
    [...] 
        prometheus:
        build: ./prometheus
        container_name: prometheus
        depends_on:
          django:
            condition: service_healthy
        networks:
          - backend
        ports:
          - "9090:9090"
    [...]

 >[!NOTE]
 >To check if the django container is healthy before running prometheus you can add this logic to your django service in your docker-compose.yml <br/>

    healthcheck:
      test: ["CMD", "curl", "-f", "localhost:8000"]  <- this will ping our app to check if it's running
      interval: 5s
      timeout: 5s
      retries: 4

## Modify your ```settings.py``` and include :

    [...]
    ALLOWED_HOSTS = ['localhost', 'django']

    INSTALLED_APPS = [
        ...
        'django_prometheus',
        ...
    ]

    MIDDLEWARE = [
        'django_prometheus.middleware.PrometheusBeforeMiddleware',
        ...
        'django_prometheus.middleware.PrometheusAfterMiddleware',
    ]

    [...]

## Modify your ```urls.py``` and include:

    [...]
    urlpatterns = [
        ...
        path('', include('django_prometheus.urls')),
    ]

## Modify your ```prometheus.yml``` and include:

    global:
      scrape_interval: 15s

    scrape_configs:
      - job_name: 'django'
        metrics_path: /metrics
        static_configs:
          - targets:
            - django:8000
            labels:
              group: 'django-app'
      [...]
>[!WARNING]
 >When you are specifying targets while using docker, you must specify your app container name with it's dedicated port (IE : ```django:8000```) and not ```localhost:8000```
 >as the container itself doesn't know any 8000 opened port, it has to use your app opened port which will be found and accessed via docker-compose

# Final Steps

You can now see metrics from your website/app by accessing the right port, here we have access on ```localhost:9090```<br/>
You can use Grafana to have a better view of those metrics.
