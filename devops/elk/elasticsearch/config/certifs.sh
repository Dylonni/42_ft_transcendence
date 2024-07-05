#! /bin/bash

    #    if [ x${ELASTIC_PASSWORD} == x ]; then
    #      echo "Set the ELASTIC_PASSWORD environment variable in the .env file";
    #      exit 1;
    #    elif [ x${KIBANA_SYSTEM_PASSWORD} == x ]; then
    #      echo "Set the KIBANA_PASSWORD environment variable in the .env file";
    #      exit 1;
    #    fi;
    #    if [ ! -f config/certs/ca.zip ]; then
    #      echo "Creating CA";
    #      bin/elasticsearch-certutil ca --silent --pem -out config/certs/ca.zip;
    #      unzip config/certs/ca.zip -d config/certs;
    #    fi;
    #    if [ ! -f config/certs/certs.zip ]; then
    #      echo "Creating certs";
    #      echo -ne \
    #      "instances:\n"\
    #      "  - name: elasticsearch\n"\
    #      "    dns:\n"\
    #      "      - elasticsearch\n"\
    #      "      - localhost\n"\
    #      "    ip:\n"\
    #      "      - 127.0.0.1\n"\
    #      "  - name: kibana\n"\
    #      "    dns:\n"\
    #      "      - kibana\n"\
    #      "      - localhost\n"\
    #      "    ip:\n"\
    #      "      - 127.0.0.1\n"\
    #      > config/certs/instances.yml;
    #      bin/elasticsearch-certutil cert --silent --pem -out config/certs/certs.zip --in config/certs/instances.yml --ca-cert config/certs/ca/ca.crt --ca-key config/certs/ca/ca.key;
    #      unzip config/certs/certs.zip -d config/certs;
    #    fi;
    #    echo "Setting file permissions"
    #    chown -R root:root config/certs;
    #    find . -type d -exec chmod 750 \{\} \;;
    #    find . -type f -exec chmod 640 \{\} \;;
    #    echo "Waiting for Elasticsearch availability";
    #    until curl -s --cacert config/certs/ca/ca.crt https://localhost:9200 | grep -q "missing authentication credentials"; do sleep 30; done;
    #    echo "Setting kibana_system password";
    #    until curl -s -X POST --cacert config/certs/ca/ca.crt -u "elastic:${ELASTIC_PASSWORD}" -H "Content-Type: application/json" https://localhost:9200/_security/user/kibana_system/_password -d "{\"password\":\"${KIBANA_SYSTEM_PASSWORD}\"}" | grep -q "^{}"; do sleep 10; done;
    #    echo "All done!";



# Ensure the script exits on any error
set -e

# Environment variable for the certificate password
# Make sure to set this environment variable before running the script
ELASTIC_CERT_PWD=${ELASTIC_CERT_PWD}

# Create CA for the cluster
echo "Creating CA for the cluster..."
./bin/elasticsearch-certutil ca --out elastic-stack-ca.p12 --pass "$ELASTIC_CERT_PWD"

# Generate certificate and key
echo "Generating certificate and key..."
./bin/elasticsearch-certutil cert --ca elastic-stack-ca.p12 --ca-pass "$ELASTIC_CERT_PWD" --out elastic-certificates.p12 --pass "$ELASTIC_CERT_PWD"

# Copy the certificate to the config directory
echo "Copying the certificate to the config directory..."
cp elastic-certificates.p12 /usr/share/elasticsearch/config/



# Ensure the Elasticsearch keystore exists before adding passwords
echo "Ensuring Elasticsearch keystore exists..."
./bin/elasticsearch-keystore create

# Add keystore and truststore passwords
echo "Adding keystore and truststore passwords..."
echo "$ELASTIC_CERT_PWD" | ./bin/elasticsearch-keystore add xpack.security.transport.ssl.keystore.secure_password --stdin
echo "$ELASTIC_CERT_PWD" | ./bin/elasticsearch-keystore add xpack.security.transport.ssl.truststore.secure_password --stdin


# # Setting file permissions for security
# echo "Setting file permissions..."
# chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config/elastic-certificates.p12
# chmod 600 /usr/share/elasticsearch/config/elastic-certificates.p12



cd /usr/share/elasticsearch/bin
./elasticsearch

# ./bin/elasticsearch


echo "Elasticsearch certificates setup completed."
