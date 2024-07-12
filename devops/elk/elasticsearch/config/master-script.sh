#! /bin/bash

#elastic search

# in elasticsearch.yml file 
# see if there is a /etc/elasticsearch directory ??
# xpack.security.enabled: true
# discovery.type: single-node




#set passwords - if needed, do the followings, with a script for interactive mode:
./bin/elasticsearch-reset-password -i -u elastic # not needed
./bin/elasticsearch-reset-password -u kibana_system


# kibana

# in kibana.yml file:
# see if there is a /etc/kibana directory ??
# elasticsearch.username: "kibana_system"


# kibana commands
./bin/kibana-keystore create
./bin/kibana-keystore add elasticsearch.password #interactive only ?



#then back to elasticsearch

./bin/elasticsearch-certutil ca #accept default name, plus set password

./bin/elasticsearch-certutil cert --ca elastic-stack-ca.p12 # asks for ca password, then create password for certificate, accept default name
#then copy the certificate to elasticsearch/conf

#add cluster name and node name to elastic yml, as well as following:
# xpack.security.transport.ssl.enabled: true
# xpack.security.transport.ssl.verification_mode: certificate 
# xpack.security.transport.ssl.client_authentication: required
# xpack.security.transport.ssl.keystore.path: elastic-certificates.p12
# xpack.security.transport.ssl.truststore.path: elastic-certificates.p12


#interactive for set password in keystore
./bin/elasticsearch-keystore add xpack.security.transport.ssl.keystore.secure_password
./bin/elasticsearch-keystore add xpack.security.transport.ssl.truststore.secure_password

# certutil as interactive script, then unzip the archive and copy files
cp <archive_path>/http.p12 elasticsearch/config/
cp <archive_path>/elasticsearch-ca.pem kibana/config/

# add following to elasticsearch.yml
# xpack.security.http.ssl.enabled: true
# xpack.security.http.ssl.keystore.path: http.p12

#add password to private key in keystore
./bin/elasticsearch-keystore add xpack.security.http.ssl.keystore.secure_password

# in kibana.yml
# elasticsearch.ssl.certificateAuthorities: $KBN_PATH_CONF/elasticsearch-ca.pem
# elasticsearch.hosts: https://localhost:9200


# in elastic container
./bin/elasticsearch-certutil csr -name kibana-server -dns localhost,www.transcendence42.rocks

#unzip archive
unzip csr-bundle.zip
#copy the .key to kibana config directory

# in kibana ?
openssl x509 -req -days 365 -in kibana-server.csr -signkey kibana-server.key -out kibana-server.crt
#copy the .crt to kibana config directory


# in kibana.yml
# server.ssl.certificate: $KBN_PATH_CONF/kibana-server.crt
# server.ssl.key: $KBN_PATH_CONF/kibana-server.key
# server.ssl.enabled: true


