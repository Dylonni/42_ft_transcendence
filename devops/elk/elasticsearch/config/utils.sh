#! /bin/bash


# echo "keys added to keystore, starting expect script"
#start expect script:
# ./script.exp
# ./cert2.sh
# ./exp2.sh
# ./certutils_http.sh



# ./bin/elasticsearch-certutil http


if ./cert2.sh; then
    echo "certutils done"
else
    echo "certutils failed"
fi

unzip elasticsearch-ssl-http.zip
cp elasticsearch/http.p12 config/http.p12
cp kibana/elasticsearch-ca.pem config/elasticsearch-ca.pem
echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.http.ssl.keystore.secure_password



./bin/elasticsearch-certutil csr -name kibana-server -dns localhost
unzip csr-bundle.zip

openssl x509 -req -days 365 -in kibana-server/kibana-server.csr -signkey kibana-server/kibana-server.key -out kibana-server.crt




touch /usr/share/elasticsearch/config/kibstart