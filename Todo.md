ensure all services have a health check
check again for ssl/tls : when/where needed
try to see if a filezilla container would work with the infinity site ?

cybersec
    nginx
        add "modsecurity on" to all config files   ==> done
        change the "return 301" into "rewrite" ?
    
    RGPD
        general
            can we decide to end/suspend/ban an account?
            look into terms of use
            can users report someone?
            for all published docs and policies : define contact email(s)
        terms of use
        PIA
        privacy policy
            !! our privacy policy does include a Cookie Policy
            define how to contact Transcendence42 : email
            where are data stored ? server or locally ?
        "feuille de route" on adding security features -> including db backup, all SOPs in case of breach etc
        ensure data is handled in an "anonymized" way
        how to contact team?
        how to request deletion of account ? (there's the button, but what about hacked accounts?)
    
    vault
        how to handle API keys for grafana ?
            -> try to have as many of the .env vars handled by vault

devops
    grafana
        finalize dashboards for django              ==> done
        add a 403-error alert (django ? modsec ?)
            -> check how to simulate sql injection, so as to show it's handled AND how alerting works

    postgres
        look into the "sslmode=disable" and how to remove it

    elk
        ? do sth ?





questions pour la team

    apres retrait des "printf debug", et sans modif du code : peut-on visualiser les donnes perso d'un compte ? (email, coa, 42id, photo profil)

    adresse courriel de contact?

reponses de la team
    pour chaque element de 42 : 
        42 id: visible par personne, suppression des que authentification ok
        photo profil, banniere coa, couleur coa : visibles par tout le mon de sur page profil
    COOKIES !! on stocke les JWT (access roken, refresh token) et preference de langue
    MaJ privacy policy : envoi auto de courriel notifiant qu'il y a eu une MaJ
