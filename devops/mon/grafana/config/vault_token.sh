#!/bin/sh

# Wait for the token file to be created
while [ ! -f /var/lib/grafana/secrets/token ]; do
  sleep 1
done

# # Read the token
TOKEN=$(cat /var/lib/grafana/secrets/token)

# Extract the token from the third line
TOKEN=$(awk 'NR==3 {print $2}' /var/lib/grafana/secrets/token)

# Update the grafana.ini file
cat <<EOF >> /etc/grafana/grafana.ini

token = $TOKEN
EOF

# Start Grafana
exec grafana-server --homepath=/usr/share/grafana