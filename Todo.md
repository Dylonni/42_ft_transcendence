ensure all services have a health check
check again for ssl/tls : when/where needed
try to see if a filezilla container would work with the infinity site ?

cybersec
    nginx
        add "modsecurity on" to all config files   ==> done
        change the "return 301" into "rewrite" ?
    
    RGPD
        PIA
        privacy notice
        "feuille de route" on adding security features -> including db backup, all SOPs in case of breach etc
        ensure data is handled in an "anonymized" way
        how to contact team? how to request deletion of account ?
    
    vault
        how to handle API keys for grafana ?
            -> try to have as many of the .env vars handled by vault

devops
    grafana
        finalize dashboards for django
        add a 403-error alert (django ? modsec ?)
            -> check how to simulate sql injection, so as to show it's handled AND how alerting works

    postgres
        look into the "sslmode=disable" and how to remove it

    elk
        ? do sth ?
