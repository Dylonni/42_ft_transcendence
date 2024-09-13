#! /bin/bash


if [ x${ELASTIC_PASSWORD} == x ]; then
    echo "ELASTIC_PASSWORD not in env";
    exit 1;
elif [ x${KIBANA_SYSTEM_PASSWORD} == x ]; then
    echo "KIBANA_SYSTEM_PASSWORD not in env";
    exit 1;
fi;

if [ ! -f /usr/share/elasticsearch/config/certs/ca.zip ]; then
    echo "Generating CA files";
    /usr/share/elasticsearch/bin/elasticsearch-certutil ca --silent --pem -out config/certs/ca.zip;
    unzip /usr/share/elasticsearch/config/certs/ca.zip -d config/certs;
fi;

if [ ! -f /usr/share/elasticsearch/config/certs/certs.zip ]; then
    echo "Generating certificates!";
    /usr/share/elasticsearch/bin/elasticsearch-certutil cert --silent --pem -out config/certs/certs.zip --in config/certs/cert.yml --ca-cert config/certs/ca/ca.crt --ca-key config/certs/ca/ca.key;
    unzip /usr/share/elasticsearch/config/certs/certs.zip -d config/certs;
fi;

echo "Setting file permissions!"
# chown -R root:root config/certs;
# find . -type d -exec chmod 750 \{\} \;;
# find . -type f -exec chmod 640 \{\} \;;
echo "Waiting for Elasticsearch availability";
until curl -s --cacert /usr/share/elasticsearch/config/certs/ca/ca.crt https://elasticsearch:9200 | grep -q "missing authentication credentials"; do sleep 30; done;
echo "Setting password of default kibana user 'kibana_system'";
until curl -s -X POST --cacert /usr/share/elasticsearch/config/certs/ca/ca.crt -u "elastic:${ELASTIC_PASSWORD}" -H "Content-Type: application/json" https://elasticsearch:9200/_security/user/kibana_system/_password -d "{\"password\":\"${KIBANA_SYSTEM_PASSWORD}\"}" | grep -q "^{}"; do sleep 10; done;
echo "Setup is done!"

# Keep the container running
tail -f /dev/null