FROM hashicorp/vault:1.17.0

COPY ./config/vault.hcl /vault/config/vault.hcl
COPY ./tools/init.sh .

EXPOSE 8125

ENTRYPOINT [ "sh", "init.sh" ]