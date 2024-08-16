# Useful commands

## log into vault
vault login
-> then enter root token from /vault/output/init.txt

## Vault tokens and accessors

### list all tokens
vault list auth/token/accessors

### see details of the accessor
vault token lookup -accessor <token accessor>

### see policies linked to a token from the list
vault write auth/token/lookup-accessor accessor=<token accessor>

### revoke token
vault write auth/token/revoke-accessor accessor=<token accessor>


### retrieve token capabilities for a given path
vault token capabilities -accessor <token accessor> <path>
	-> for the path, try either sys/auth/approle (should work) or identity/identity (should be denied)




## Vault policies
### list all policies
vault policy list

### display a policy
vault policy read <policy name>

### check policy needed
to check the policy needed for kv put or kv get, add "-output-policy" as option
=> for instance the cmd (this is TESTED)
		vault kv put -output-policy -mount=secret django/key SECRET_KEY="${DJANGO_SECRET_KEY}"
	will output :
path "secret/data/django/key" {
  capabilities = ["create", "update"]

the cmd (this is TESTED)
		vault kv get -output-policy -mount=secret django/key
	will output
path "secret/data/django/key" {
  capabilities = ["read"]
}



## Vault secrets

## write a secret
vault kv put -mount=secret <path> key_1="value_1" key_2="value_2"
	-> must supply at least 1 key-value set
	-> a path can only store one secret, so creating a secret at the same path will overwrite earlier version

## update/modify a secret
vault kv patch -mount=secret mon/prometheus testkey="testvalue"
	-> if there is already a key with same name, it will overwrite ("patch") the existing corresponding value
	-> if there is no such key, it will add the key-value set to the existing secret

### retrieve info for a given secret
vault kv get -mount=secret <path>


### delete a secret
#### delete data associated to a secret but keep the secret
vault kv delete -mount=secret <path>
#### fully destroy a secret
vault kv metadata delete -mount=secret <path>















# below needs to be checked :








