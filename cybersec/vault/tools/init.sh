#!/bin/sh

vault server -config=/vault/config/vault.hcl &
sleep 5

mkdir -p /vault/output
mkdir -p /vault/secrets/django

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

    echo "Generate temporary tokens for other services..."
    vault policy write django-policy /vault/config/policies/django-policy.hcl
    vault token create -ttl=1h -policy=django-policy > /vault/secrets/django/token

    # echo "Sealing Vault..."
    # vault operator seal
fi

touch /vault/output/initialized

tail -f /dev/null