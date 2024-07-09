ARG ELK_STACK_VERSION
ARG ELASTIC_PASSWORD


FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_STACK_VERSION}

RUN mkdir -p /usr/share/elasticsearch/config/certs
RUN ./bin/elasticsearch-certutil ca --out /usr/share/elasticsearch/config/elastic-stack-ca.p12 --pass "${ELASTIC_PASSWORD}" --silent
RUN ./bin/elasticsearch-certutil cert --ca /usr/share/elasticsearch/config/elastic-stack-ca.p12 --ca-pass "${ELASTIC_PASSWORD}" --out /usr/share/elasticsearch/config/elastic-certificates.p12  --pass "${ELASTIC_PASSWORD}" --silent
# RUN cp /usr/share/elasticsearch/config/elastic-stack-ca.p12 /usr/share/elasticsearch/config/

RUN ./bin/elasticsearch-keystore create
RUN echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.keystore.secure_password
RUN echo "${ELASTIC_PASSWORD}" | ./bin/elasticsearch-keystore add --stdin xpack.security.transport.ssl.truststore.secure_password



USER root

RUN apt-get update && \
    apt-get install -y sudo expect && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# RUN usermod -aG sudo elasticsearch

# RUN echo "elasticsearch:${ELASTIC_PASSWORD}" | chpasswd

RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config/

COPY ./config/certutils.sh /usr/share/elasticsearch/certutils.sh
RUN chmod +x /usr/share/elasticsearch/certutils.sh

USER elasticsearch

# RUN echo "" | ./bin/elasticsearch-keystore add --stdin xpack.security.http.ssl.keystore.secure_password

RUN /usr/share/elasticsearch/certutils.sh

# COPY ./config/http.p12 /usr/share/elasticsearch/config/http.p12
COPY ./config/cert.yml /usr/share/elasticsearch/config/cert.yml
# RUN bin/elasticsearch-certutil http --batch --config /usr/share/elasticsearch/config/cert.yml -out /usr/share/elasticsearch/elasticsearch-ssl-http.zip
# RUN bin/elasticsearch-certutil http /usr/share/elasticsearch/config/cert.yml -v
# RUN echo "${ELASTIC_PASSWORD}" | bin/elasticsearch-certutil http --in config/cert.yml -out elasticsearch-ssl-http.zip --days 90 --ca /usr/share/elasticsearch/config/elastic-stack-ca.p12 --ca-pass "${ELASTIC_PASSWORD}"

# RUN unzip /usr/share/elasticsearch/elasticsearch-ssl-http.zip -d /usr/share/elasticsearch/

# RUN cp /usr/share/elasticsearch/elasticsearch-ssl-http/elasticsearch/http.p12 /usr/share/elasticsearch/config/http.p12

# RUN ./bin/elasticsearch-certutil http --silent --in /usr/share/elasticsearch/config/certs.yml \
#     && echo "Setting up keystore" \
#     && (echo "your_keystore_password"; echo "your_keystore_password") | ./bin/elasticsearch-keystore add xpack.security.http.ssl.keystore.secure_password
# RUN expect -c "\
#     spawn ./bin/elasticsearch-certutil http ; \
# 	expect \"Generate a CSR? [y/N]\"; \
# 	send \"n\r\"; \
# 	expect \"Use an existing CA? [y/N]\"; \
# 	send \"y\r\"; \
# 	expect \"CA Path:\"; \
# 	send \"/usr/share/elasticsearch/config/elastic-stack-ca.p12\r\"; \
# 	expect \"Password for elastic-stack-ca.p12:\"; \
# 	send \"\r\"; \
# 	expect \"For how long should your certificate be valid? [5y]\"; \
# 	send \"90d\r\"; \
# 	expect \"Generate a certificate per node? [y/N]\"; \
# 	send \"n\r\"; \
# 	expect \"When you are done, press <ENTER> once more to move on to the next step.\"; \
# 	send \"localhost\r\"; \
# 	send \"transcendence42\r\"; \
# 	send \"transcendence42.rocks\r\"; \
# 	send \"\r\"; \
# 	expect \"Is this correct [Y/n]\"; \
# 	send \"y\r\"; \
# 	expect \"When you are done, press <ENTER> once more to move on to the next step.\"; \
# 	send \"127.0.0.1\r\"; \
# 	send \"\r\"; \
# 	expect \"Is this correct [Y/n]\"; \
# 	send \"y\r\"; \
# 	expect \"Do you wish to change any of these options? [y/N]\"; \
# 	send \"n\r\"; \
# 	expect \"Provide a password for the "http.p12" file:  [<ENTER> for none]\"; \
# 	send \"${ELASTIC_PASSWORD}\r\"; \
# 	expect \"Repeat password to confirm:\"; \
# 	send \"${ELASTIC_PASSWORD}\r\"; \
# 	expect \"What filename should be used for the output zip file? [/usr/share/elasticsearch/elasticsearch-ssl-http.zip]\"; \
# 	send \"/usr/share/elasticsearch/elasticsearch-ssl-http.zip\r\"; \
#     interact"


# RUN expect -c "\
#     set timeout 60; \
#     spawn ./bin/elasticsearch-certutil http ; \
#     expect { \
#         \"Generate a CSR? [y/N]\" { \
#             send \"n\r\"; \
#             exp_continue; \
#         } \
#         \"Use an existing CA? [y/N]\" { \
#             send \"y\r\"; \
#             exp_continue; \
#         } \
#         \"CA Path:\" { \
#             send \"/usr/share/elasticsearch/config/elastic-stack-ca.p12\r\"; \
#             exp_continue; \
#         } \
#         \"Password for elastic-stack-ca.p12:\" { \
#             send \"\r\"; \
#             exp_continue; \
#         } \
#         \"For how long should your certificate be valid? [5y]\" { \
#             send \"90d\r\"; \
#             exp_continue; \
#         } \
#         timeout { \
#             puts \"Operation timed out\"; \
#             exit 1; \
#         } \
#         eof { \
#             puts \"Unexpected end of file or error\"; \
#             exit 1; \
#         } \
#         \"Generate a certificate per node? [y/N]\" { \
#             send \"n\r\"; \
#             exp_continue; \
#         } \
#         \"When you are done, press <ENTER> once more to move on to the next step.\" { \
#             send \"localhost\r\"; \
#             send \"transcendence42\r\"; \
#             send \"transcendence42.rocks\r\"; \
#             send \"\r\"; \
#             exp_continue; \
#         } \
#         \"Is this correct [Y/n]\" { \
#             send \"y\r\"; \
#             exp_continue; \
#         } \
#         \"When you are done, press <ENTER> once more to move on to the next step.\" { \
#             send \"127.0.0.1\r\"; \
#             send \"\r\"; \
#             exp_continue; \
#         } \
#         \"Is this correct [Y/n]\" { \
#             send \"y\r\"; \
#             exp_continue; \
#         } \
#         \"Do you wish to change any of these options? [y/N]\" { \
#             send \"n\r\"; \
#             exp_continue; \
#         } \
#         \"Provide a password for the http.p12 file:  [<ENTER> for none]\" { \
#             send \"${ELASTIC_PASSWORD}\r\"; \
#             exp_continue; \
#         } \
#         \"Repeat password to confirm:\" { \
#             send \"${ELASTIC_PASSWORD}\r\"; \
#             exp_continue; \
#         } \
#         \"What filename should be used for the output zip file? [/usr/share/elasticsearch/elasticsearch-ssl-http.zip]\" { \
#             send \"/usr/share/elasticsearch/elasticsearch-ssl-http.zip\r\"; \
#         } \
#         default { \
#             puts \"Unexpected output\"; \
#             exit 1; \
#         } \
#     };"

# RUN expect -c "\
#     spawn ./bin/elasticsearch-certutil http ; \
#     expect \"Enter keystore password:\"; \
#     send \"\r\"; \
#     expect \"Again:\"; \
#     send \"\r\"; \
#     interact"



COPY ./config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
# COPY ./config/certifs.sh /usr/local/bin/certifs.sh
# RUN chmod +x /usr/local/bin/certifs.sh

# ENTRYPOINT [ "bash", "certifs.sh" ]

# COPY ./config/certifs.sh /usr/share/elasticsearch/certifs.sh
# RUN chmod +x /usr/share/elasticsearch/certifs.sh

# RUN bin/elasticsearch-reset-password -u elastic -y

# ENTRYPOINT ["/bin/bash", "/usr/share/elasticsearch/certifs.sh"]
