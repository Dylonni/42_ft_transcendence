#!/usr/bin/expect -f

set timeout 60
set elastic_password $env(ELASTIC_PASSWORD)
spawn ./bin/elasticsearch-certutil http
expect {
    "Generate a CSR? [y/N]" {
        send "n\r"
        exp_continue
    }
    "Use an existing CA? [y/N]" {
        send "y\r"
        exp_continue
    }
    "CA Path:" {
        send "/usr/share/elasticsearch/config/elastic-stack-ca.p12\r"
        exp_continue
    }
    "Password for elastic-stack-ca.p12:" {
        send "\r"
        exp_continue
    }
    "For how long should your certificate be valid? [5y]" {
        send "90d\r"
        exp_continue
    }
    timeout {
        puts "Operation timed out"
        exit 1
    }
    eof {
        puts "Unexpected end of file or error"
        exit 1
    }
    "Generate a certificate per node? [y/N]" {
        send "n\r"
        exp_continue
    }
    "When you are done, press <ENTER> once more to move on to the next step." {
        send "localhost\r"
        send "transcendence42\r"
        send "transcendence42.rocks\r"
        send "\r"
        exp_continue
    }
    "Is this correct [Y/n]" {
        send "y\r"
        exp_continue
    }
    "When you are done, press <ENTER> once more to move on to the next step." {
        send "127.0.0.1\r"
        send "\r"
        exp_continue
    }
    "Is this correct [Y/n]" {
        send "y\r"
        exp_continue
    }
    "Do you wish to change any of these options? [y/N]" {
        send "n\r"
        exp_continue
    }
    "Provide a password for the http.p12 file:  [<ENTER> for none]" {
        send "$elastic_password\r"
        exp_continue
    }
    "Repeat password to confirm:" {
        send "$elastic_password\r"
        exp_continue
    }
    "What filename should be used for the output zip file? [/usr/share/elasticsearch/elasticsearch-ssl-http.zip]" {
        send "/usr/share/elasticsearch/elasticsearch-ssl-http.zip\r"
    }
    default {
        puts "Unexpected output"
        exit 1
    }
}