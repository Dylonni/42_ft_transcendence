#!/bin/sh

vault server -config=/vault/config/vault.hcl &
sleep 5

mkdir -p /vault/output
mkdir -p /vault/secrets/django
mkdir -p /vault/secrets/mon/grafana

if vault status | grep -q 'Initialized.*true'; then
    echo "Vault is already initialized."
else
    echo "Initializing Vault..."
    vault operator init -key-shares=1 -key-threshold=1 > /vault/output/init.txt
	UNSEAL_KEY=$(grep 'Unseal Key 1:' /vault/output/init.txt | awk '{print $NF}')
	ROOT_TOKEN=$(grep 'Initial Root Token:' /vault/output/init.txt | awk '{print $NF}')

	echo "Unsealing Vault..."
    vault operator unseal $UNSEAL_KEY

    echo "Logging in with root token..."
    export VAULT_TOKEN=$ROOT_TOKEN

    echo "Enabling KV-v2 secrets engine..."
    vault secrets enable -path=secret kv-v2

	echo "Storing secrets..."
    vault kv put -mount=secret django/key SECRET_KEY="${DJANGO_SECRET_KEY}"

    vault kv put -mount=secret mon/prometheus PROM_DB="${PROMETHEUS_DB}" PROM_USER="${PROMETHEUS_USER}" PROM_PASS="${PROMETHEUS_PASSWORD}"
    vault kv put -mount=secret mon/pg_exporter DATA_SOURCE_NAME="${DATA_SOURCE_NAME}"
    vault kv put -mount=secret mon/grafana GF_USER="${GF_SECURITY_ADMIN_USER}" GF_PASS="${GF_SECURITY_ADMIN_PASSWORD}"


    echo "Generate temporary tokens for other services..."
    vault policy write django-policy /vault/config/policies/django-policy.hcl
    vault token create -ttl=1h -policy=django-policy -display-name=django > /vault/secrets/django/token

    vault policy write admin-policy /vault/config/policies/admin-policy.hcl
    vault token create -policy=admin-policy -display-name=admin > /vault/output/admin.txt



    # Check if the vault command was successful
    if [ $? -eq 0 ]; then
        echo "Vault command executed successfully."
    else
        echo "Vault command failed to execute." >&2
        exit 1
    fi

    # Check if the token file is not empty
    if [ -s /vault/secrets/django/token ]; then
        echo "Token was successfully created."
    else
        echo "Token file is empty." >&2
        exit 1
    fi

    # echo "Sealing Vault..."
    # vault operator seal
fi

touch /vault/output/initialized

tail -f /dev/null