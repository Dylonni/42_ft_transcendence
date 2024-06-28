FROM hashicorp/vault:1.17.0

RUN mkdir -p /vault/config/policies

COPY ./config/vault.hcl /vault/config/vault.hcl
COPY ./config/policies/django-policy.hcl /vault/config/policies/django-policy.hcl
COPY ./tools/init.sh .

EXPOSE 8125

ENTRYPOINT [ "sh", "init.sh" ]