#! /bin/bash


# Ensure the script exits on any error
# set -e


# Set variables
set timeout -1
set elastic_user "elastic"
set new_password ${ELASTIC_PASSWORD}


# expect <<EOF
# set timeout -1
# spawn /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -i
# expect "Continue with password reset? \[y/N\]"
# send -- "y\r"
# expect "Enter new password for the elastic user: "
# send -- "${ELASTIC_PASSWORD}\r"
# expect "Re-enter new password for the elastic user: "
# send -- "${ELASTIC_PASSWORD}\r"
# expect eof
# EOF

## confirm the password was reset:
#### Password for the [elastic] user successfully reset.






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


