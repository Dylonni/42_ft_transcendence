FROM owasp/modsecurity-crs:4.3.0-nginx-alpine-202406090906

USER root
RUN apk update && apk upgrade && apk add --no-cache openssl


COPY ./conf/ssl_nginx.conf /etc/nginx/templates/conf.d/default.conf.template
COPY ./conf/modsecurity.conf /etc/nginx/templates/modsecurity.d/modsecurity-override.conf.template


EXPOSE 8080 8443