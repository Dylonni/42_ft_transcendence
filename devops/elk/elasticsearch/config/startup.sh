#!/bin/bash


if [ -z "$ELASTIC_PASSWORD" ]; then echo "ELASTIC_PASSWORD is not set" && exit 1; else echo "ELASTIC_PASSWORD is set to '$ELASTIC_PASSWORD'"; fi



if [ ! -f /usr/share/elasticsearch/config/kibstart ] ; then

	./bin/elasticsearch-certutil ca --out /usr/share/elasticsearch/config/elastic-stack-ca.p12 --pass "${ELASTIC_PASSWORD}" --silent

	./bin/elasticsearch-certutil cert --ca /usr/share/elasticsearch/config/elastic-stack-ca.p12 --ca-pass "${ELASTIC_PASSWORD}" --out /usr/share/elasticsearch/config/elastic-certificates.p12  --pass "${ELASTIC_PASSWORD}" --silent


	echo "adding keys to keystore"
	./bin/elasticsearch-keystore create
	echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.keystore.secure_password
	echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.truststore.secure_password
fi



#then in container start utils.sh

# Keep the container running
tail -f /dev/null