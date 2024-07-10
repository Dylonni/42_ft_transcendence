#!/bin/bash

unzip elasticsearch-ssl-http.zip;
cp -r elasticsearch/http.p12 .;


# if [ ! -f elasticsearch-ssl-http.zip ]; then
#     echo "File elasticsearch-ssl-http.zip not found!"
#     exit 1
# fi

# unzip elasticsearch-ssl-http.zip || { echo "Failed to unzip file"; exit 1; }
