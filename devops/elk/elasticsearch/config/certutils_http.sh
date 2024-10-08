#!/usr/bin/expect -f

set timeout -1
# Print all environment variables
# puts "Printing all environment variables";
# foreach name [array names env] {
#     puts "$name: $env($name)"
# }
# puts "Printing all environment variables done";



# set force_conservative 0  ;# set to 1 to force conservative mode even if
# 			  ;# script wasn't run conservatively originally
# if {$force_conservative} {
# 	set send_slow {1 .1}
# 	proc send {ignore arg} {
# 		sleep .1
# 		exp_send -s -- $arg
# 	}
# }


# set elastic_password $env(ELASTIC_PASSWORD)
set completed 0
exp_internal 1
spawn ./bin/elasticsearch-certutil http
match_max 100000

expect "\r
## Elasticsearch HTTP Certificate Utility\r
\r
The 'http' command guides you through the process of generating certificates\r
for use on the HTTP (Rest) interface for Elasticsearch.\r
\r
This tool will ask you a number of questions in order to generate the right\r
set of files for your needs.\r
\r
## Do you wish to generate a Certificate Signing Request (CSR)?\r
\r
A CSR is used when you want your certificate to be created by an existing\r
Certificate Authority (CA) that you do not control (that is, you don't have\r
access to the keys for that CA). \r
\r
If you are in a corporate environment with a central security team, then you\r
may have an existing Corporate CA that can generate your certificate for you.\r
Infrastructure within your organisation may already be configured to trust this\r
CA, so it may be easier for clients to connect to Elasticsearch if you use a\r
CSR and send that request to the team that controls your CA.\r
\r
If you choose not to generate a CSR, this tool will generate a new certificate\r
for you. That certificate will be signed by a CA under your control. This is a\r
quick and easy way to secure your cluster with TLS, but you will need to\r
configure all your clients to trust that custom CA.\r
\r
Generate a CSR?"

# expect -exact "Generate a CSR?"


send -- "n\r"
expect "n\r\r
## Do you have an existing Certificate Authority (CA) key-pair that you wish to use to sign your certificate?\r
\r
If you have an existing CA certificate and key, then you can use that CA to\r
sign your new http certificate. This allows you to use the same CA across\r
multiple Elasticsearch clusters which can make it easier to configure clients,\r
and may be easier for you to manage.\r
\r
If you do not have an existing CA, one will be generated for you.\r
\r
Use an existing CA? \[y/N\]"
send -- "y\r"
expect "y\r\r
## What is the path to your CA?\r
\r
Please enter the full pathname to the Certificate Authority that you wish to\r
use for signing your new http certificate. This can be in PKCS#12 (.p12), JKS\r
(.jks) or PEM (.crt, .key, .pem) format.\r
CA Path: "
send -- "usr/share/elasticsearch/config/elastic-stack-ca.p12\r"
expect "/usr/share/elasticsearch/config/elastic-stack-ca.p12\r"
send -- "\r"
expect "/usr/share/elasticsearch/config/elastic-stack-ca.p12\r\r
Reading a PKCS12 keystore requires a password.\r
It is possible for the keystore's password to be blank,\r
in which case you can simply press <ENTER> at the prompt\r
Password for elastic-stack-ca.p12:"
send -- "$env(ELASTIC_PASSWORD)\r"
expect -exact "\r\r
## How long should your certificates be valid?\r
\r
Every certificate has an expiry date. When the expiry date is reached clients\r
will stop trusting your certificate and TLS connections will fail.\r
\r
Best practice suggests that you should either:\r
(a) set this to a short duration (90 - 120 days) and have automatic processes\r
to generate a new certificate before the old one expires, or\r
(b) set it to a longer duration (3 - 5 years) and then perform a manual update\r
a few months before it expires.\r
\r
You may enter the validity period in years (e.g. 3Y), months (e.g. 18M), or days (e.g. 90D)\r
\r
For how long should your certificate be valid? \[5y\] "
send -- "90d\r"
expect -exact "90d\r\r
## Do you wish to generate one certificate per node?\r
\r
If you have multiple nodes in your cluster, then you may choose to generate a\r
separate certificate for each of these nodes. Each certificate will have its\r
own private key, and will be issued for a specific hostname or IP address.\r
\r
Alternatively, you may wish to generate a single certificate that is valid\r
across all the hostnames or addresses in your cluster.\r
\r
If all of your nodes will be accessed through a single domain\r
(e.g. node01.es.example.com, node02.es.example.com, etc) then you may find it\r
simpler to generate one certificate with a wildcard hostname (*.es.example.com)\r
and use that across all of your nodes.\r
\r
However, if you do not have a common domain name, and you expect to add\r
additional nodes to your cluster in the future, then you should generate a\r
certificate per node so that you can more easily generate new certificates when\r
you provision new nodes.\r
\r
Generate a certificate per node? \[y/N\]"
send -- "n\r"
expect -exact "n\r\r
## Which hostnames will be used to connect to your nodes?\r
\r
These hostnames will be added as \"DNS\" names in the \"Subject Alternative Name\"\r
(SAN) field in your certificate.\r
\r
You should list every hostname and variant that people will use to connect to\r
your cluster over http.\r
Do not list IP addresses here, you will be asked to enter them later.\r
\r
If you wish to use a wildcard certificate (for example *.es.example.com) you\r
can enter that here.\r
\r
Enter all the hostnames that you need, one per line.\r
When you are done, press <ENTER> once more to move on to the next step.\r
\r"
send -- "localhost\r"
expect -exact "localhost"

send -- "transcendence42\r"
expect -exact "transcendence42"

send -- "transcendence42.rocks\r"
expect -exact "transcendence42.rocks"

expect -exact "\r\r
You entered the following hostnames.\r
\r
 - localhost\r
 - transcendence42\r
 - transcendence42.rocks\r
\r
Is this correct \[Y/n\]"
send -- "y\r"
expect -exact "y\r\r
## Which IP addresses will be used to connect to your nodes?\r
\r
If your clients will ever connect to your nodes by numeric IP address, then you\r
can list these as valid IP \"Subject Alternative Name\" (SAN) fields in your\r
certificate.\r
\r
If you do not have fixed IP addresses, or not wish to support direct IP access\r
to your cluster then you can just press <ENTER> to skip this step.\r
\r
Enter all the IP addresses that you need, one per line.\r
When you are done, press <ENTER> once more to move on to the next step.\r
\r"
send -- "127.0.0.1\r"
expect -exact "127.0.0.1\r\r"
send -- "\r"
expect -exact "\r\r
You entered the following IP addresses.\r
\r
 - 127.0.0.1\r
\r
Is this correct \[Y/n\]"
send -- "y\r"
expect -exact "y\r\r
## Other certificate options\r
\r
The generated certificate will have the following additional configuration\r
values. These values have been selected based on a combination of the\r
information you have provided above and secure defaults. You should not need to\r
change these values unless you have specific requirements.\r
\r
Key Name: localhost\r
Subject DN: CN=localhost\r
Key Size: 2048\r
\r
Do you wish to change any of these options? \[y/N\]"
send -- "n\r"
expect -exact "n\r\r
## What password do you want for your private key(s)?\r
\r
Your private key(s) will be stored in a PKCS#12 keystore file named \"http.p12\".\r
This type of keystore is always password protected, but it is possible to use a\r
blank password.\r
\r
If you wish to use a blank password, simply press <enter> at the prompt below.\r
Provide a password for the \"http.p12\" file:  \[<ENTER> for none\]"
send -- "$env(ELASTIC_PASSWORD)\r"
expect -exact "\r\r
Repeat password to confirm: "
send -- "$env(ELASTIC_PASSWORD)\r"
expect -exact "\r\r
## Where should we save the generated files?\r
\r
A number of files will be generated including your private key(s),\r
public certificate(s), and sample configuration options for Elastic Stack products.\r
\r
These files will be included in a single zip archive.\r
\r
hWhat filename should be used for the output zip file? \[/usr/share/elasticsearch/elasticsearch-ssl-http.zip\] "
send -- "/usr/share/elasticsearch/elasticsearch-ssl-http.zip\r"
expect -exact "/usr/share/elasticsearch/elasticsearch-ssl-http.zip\r"
send -- "\r"
expect eof
