# Installation Process

Your logstash folder should contain 2 folders and 3 files : <br/>
        📂config<br/>
       └ logstash.yml<br/>
        📂pipeline<br/>
       └ logstash.conf<br/>
  🐋Dockerfile

Inside your django app folder, install logstash_formatter <br/>
```$ pipenv install logstash-formatter```

# ```Dockerfile``` should contain:
      ARG ELK_STACK_VERSION
      FROM docker.elastic.co/logstash/logstash:${ELK_STACK_VERSION}
      COPY ./pipeline/logstash.conf /usr/share/logstash/pipeline/logstash.conf
      [...]

# ```docker-compose.yml``` should contain:
    [...] 
    logstash:
      build:
        context: ./logstash
        args:
          ELK_STACK_VERSION: ${ELK_STACK_VERSION}
      container_name: logstash
      environment:
        LS_JAVA_OPTS: -Xms256m -Xmx256m
        LOGSTASH_INTERNAL_PASSWORD: ${LOGSTASH_INTERNAL_PASSWORD:-}
      depends_on:
        - elasticsearch
      networks:
        - backend
        - elk
      ports:
        - "5000:5000"
    [...]

# Modify your ```logstash.yml``` and include :
      http.host: 0.0.0.0
      
      node.name: logstash
      xpack.monitoring.enabled: true
    [...]
    
# Modify your ```logstash.conf``` and include :
      input {
        tcp {
          port => 5000
          codec => json
        }
      }

      output {
        elasticsearch {
          hosts => ["elasticsearch:9200"]
          index => "django-logs-%{+YYYY.MM.dd}"
        }
      }
      [...]
>[!NOTE]
>This file is needed to configure where logstash should listen to JSON messages, and where it should connect to send the messages after they have been treated. We recieve them at port ```5000``` and send them to elasticsearch at port ```9200```.

# Modify your ```settings.py``` and include :
      [...]
      LOGGING = {
          'version': 1,
          'disable_existing_loggers': False,
          'handlers': {
              'logstash': {
                  'level': 'DEBUG',
                  'class': 'logging.handlers.SocketHandler',
                  'host': 'logstash',
                  'port': 5000,
                  'formatter': 'json',
              },
              'console': {
                  'level': 'DEBUG',
                  'class': 'logging.StreamHandler',
                  'formatter': 'json',
              },
      		'file': {
                  'level': 'DEBUG',
                  'class': 'logging.FileHandler',
                  'filename': '/django/debug.log',
                  'formatter': 'json',
              },
          },
          'formatters': {
              'json': {
                  '()': 'logstash_formatter.LogstashFormatter',
              },
          },
          'loggers': {
              'django': {
                  'handlers': ['logstash', 'console', 'file'],
                  'level': 'DEBUG',
                  'propagate': True,
              },
          },
      }
# Modify your ```urls.py``` and include:
      from your_app.views import home_view

      urlpatterns = [
          ...
          path('', home_view, name='home'),
      ]
>[!NOTE]
>We import our view named home_view and set a path for everytime that someone reaches ```localhost:8000```, a log is created. Then it will be handled by our logger and sent to ```elasticsearch:9200``` .

# Create a view in ```views.py``` :

      from django.shortcuts import render
      from django.http import HttpResponse
      import logging

      logger = logging.getLogger('django')

      def home_view(request):
          logger.info('User accessed the homepage')
          return HttpResponse("Welcome to the homepage!")
