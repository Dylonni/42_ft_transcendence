FROM hashicorp/vault:1.17.0



RUN apk add --no-cache openssl

RUN openssl req -x509 -nodes -days 365 -sha256 -newkey rsa:2048 -keyout /etc/ssl/nginx_selfsigned.key  -out /etc/ssl/nginx_selfsigned.crt -subj "/C=FR/ST=IDF/L=Paris/O=Ecole42/OU=Stud/CN=ft_transcendence"


RUN mkdir -p /vault/config/policies

COPY ./config/vault.hcl /vault/config/vault.hcl
COPY ./config/policies/django-policy.hcl /vault/config/policies/django-policy.hcl
COPY ./config/policies/admin-policy.hcl /vault/config/policies/admin-policy.hcl

COPY ./tools/init.sh .



# COPY ./config/certs/ /etc/ssl/certs/


EXPOSE 8125

ENTRYPOINT [ "sh", "init.sh" ]