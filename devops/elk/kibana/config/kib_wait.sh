#!/bin/bash


FILE_PATH="/usr/share/kibana/config/kibstart"

# Wait for the kibstart file to be created in the shared volume
echo "Waiting for kibstart file to be created at ${FILE_PATH}..."
while [ ! -f "$FILE_PATH" ]; do
  sleep 1
done

echo "kibstart file found. Proceeding with the main process..."


# Once the condition is met, continue with the main process
exec "$@"