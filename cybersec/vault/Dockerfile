FROM hashicorp/vault:1.17.0


RUN mkdir -p /etc/ssl/shared && mkdir -p /vault/config/policies

RUN apk add --no-cache openssl jq ca-certificates

RUN openssl req -x509 -nodes -days 365 -sha256 -newkey rsa:2048 -keyout /etc/ssl/shared/nginx_selfsigned.key -out /etc/ssl/shared/nginx_selfsigned.crt -subj "/C=FR/ST=IDF/L=Paris/O=Ecole42/OU=Stud/CN=ft_transcendence" && chmod 644 /etc/ssl/shared/nginx_selfsigned.key

COPY ./config/ /vault/config/

COPY ./tools/init.sh .

EXPOSE 8125

ENTRYPOINT [ "sh", "init.sh" ]