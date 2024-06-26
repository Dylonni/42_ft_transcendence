#!/bin/sh

vault server -config=/vault/config/vault.hcl &
sleep 5

mkdir -p /vault/output

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

    echo "Enabling KV secrets engine..."
    vault secrets enable -path=secret kv

	echo "Storing secrets..."
    vault kv put secret/django/key SECRET_KEY="${DJANGO_SECRET_KEY}"

    # echo "Sealing Vault..."
    # vault operator seal
fi

touch /vault/output/initialized

tail -f /dev/null