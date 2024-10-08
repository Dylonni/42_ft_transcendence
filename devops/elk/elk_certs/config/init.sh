#! /bin/bash


if [ x${ELASTIC_PASSWORD} == x ]; then
    echo "ELASTIC_PASSWORD not in env";
    exit 1;
elif [ x${KIBANA_SYSTEM_PASSWORD} == x ]; then
    echo "KIBANA_SYSTEM_PASSWORD not in env";
    exit 1;
fi;

if [ ! -f config/certs/ca.zip ]; then
    echo "Generating CA files";
    bin/elasticsearch-certutil ca --silent --pem -out config/certs/ca.zip;
    unzip config/certs/ca.zip -d config/certs;
fi;

if [ ! -f config/certs/certs.zip ]; then
    echo "Generating certificates!";
    bin/elasticsearch-certutil cert --silent --pem -out config/certs/certs.zip --in config/certs/cert.yml --ca-cert config/certs/ca/ca.crt --ca-key config/certs/ca/ca.key;
    unzip config/certs/certs.zip -d config/certs;
fi;

echo "Setting file permissions!"
chown -R root:root config/certs;
find . -type d -exec chmod 750 \{\} \;;
find . -type f -exec chmod 640 \{\} \;;
echo "Waiting for Elasticsearch availability";
until curl -s --cacert config/certs/ca/ca.crt http://localhost:9200 | grep -q "missing authentication credentials"; do sleep 30; done;
echo "Setting password of default kibana user 'kibana_system'";
until curl -s -X POST --cacert config/certs/ca/ca.crt -u "elastic:${ELASTIC_PASSWORD}" -H "Content-Type: application/json" http://localhost:9200/_security/user/kibana_system/_password -d "{\"password\":\"${KIBANA_SYSTEM_PASSWORD}\"}" | grep -q "^{}"; do sleep 10; done;
echo "Setup is done!"