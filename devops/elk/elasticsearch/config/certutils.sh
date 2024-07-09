#!/usr/bin/expect -f

set timeout 60
set elastic_password $env(ELASTIC_PASSWORD)
set completed 0
spawn ./bin/elasticsearch-certutil http
expect {
    "Generate a CSR?" {
        send "n\r"
        exp_continue
    }
    "Use an existing CA?" {
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
    "For how long should your certificate be valid?" {
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
    "Generate a certificate per node?" {
        send "n\r"
        exp_continue
    }
    "Enter all the hostnames *When you are done, press <ENTER> once more to move on to the next step." {
        send "localhost\r"
        send "transcendence42\r"
        send "transcendence42.rocks\r"
        send "\r"
        exp_continue
    }
    "Is this correct" {
        send "y\r"
        exp_continue
    }
    "Enter all the IP addresses *When you are done, press <ENTER> once more to move on to the next step." {
        send "127.0.0.1\r"
        send "\r"
        exp_continue
    }
    "Is this correct" {
        send "y\r"
        exp_continue
    }
    "Do you wish to change any of these options?" {
        send "n\r"
        exp_continue
    }
    -re {Provide a password for the "http\.p12" file:} {
        send "$\r"
        exp_continue
    }
    "Repeat password to confirm:" {
        send "$\r"
        exp_continue
    }
    "What filename should be used for the output zip file?" {
        send "/usr/share/elasticsearch/elasticsearch-ssl-http.zip\r"
        exp_continue
    }
    "Zip file written to /usr/share/elasticsearch/elasticsearch-ssl-http.zip" {
        set completed 1
    }
    eof {
        if {$completed} {
            puts "Completed successfully"
        } else {
            puts "Unexpected end of file"
            exit 1
        }
    }
    default {
        if {!$completed} {
            puts "Unexpected output"
            exit 1
        }
    }
}