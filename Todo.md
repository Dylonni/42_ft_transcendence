
ensure all services have a health check
try to see if a filezilla container would work with the infinity site ?
clean dockerfiles
check on both docker-compose files if we can use "expose" instead of "ports"



on bottom of all pages, should be
    privacy + cookie policy
    terms of use
    contact ?


MICROSERVICES
    use redis?
    Inter Process Communication : how to set it up ?


how long should we keep live chats ? (twitch keeps them minimum 7 days, depending on user status)

look into openclassrooms for api rest


web/django/pong/settings.py
    => look into the logging part (line 291), reconfigure to use loki instead of logstash
    => look into ssl settings ? (line 323)



cybersec
    nginx
        add "modsecurity on" to all config files   ==> done

    
    RGPD
        general
            can we decide to end/suspend/ban an account?
            look into terms of use
            can users report someone?
            for all published docs and policies : define contact email(s)
        terms of use                            ==> part 1 ok, part 2 is review
        PIA
        privacy policy
            !! our privacy policy does include a Cookie Policy
            define how to contact Transcendence42 : email
            where are data stored ? server or locally ?
        "feuille de route" on adding security features -> including db backup, all SOPs in case of breach etc
        ensure data is handled in an "anonymized" way
        how to contact team?
        how to request deletion of account ? (there's the button, but what about hacked accounts?)
        !! convert Privacy policy and TOS to html


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
        peut-on acceder au contenu des chats? des DMs?

    adresse courriel de contact?

reponses de la team
    pour chaque element de 42 : 
        42 id: visible par personne, suppression des que authentification ok
        photo profil, banniere coa, couleur coa : visibles par tout le mon de sur page profil
    COOKIES !! on stocke les JWT (access roken, refresh token) et preference de langue
    MaJ privacy policy : envoi auto de courriel notifiant qu'il y a eu une MaJ



    LOGIN
- [X] Create a template for "forgot password" (mail input)
- [X] Create a template for "confirm new password" (password input) -> create a show password button
- [X] Make the "show password" work
- [X] Create Divs to load upon error codes
- [ ] Do not redirect when forgot password email has been sent
- [X] Fix toast

    NAVBAR
- [ ] Rework the navbar by adding a page to localplay
- [ ] Make the navbar show icons depending on context

    HOME
- [X] Create a modal for "Create GameRoom"
- [X] Add dropdown for languages (FR, EN, JP)
- [X] Move Player search to the right side
- [X] Add a background for "Search Game"
- [X] Remove the "Stats Indicator" , Create a Rank indicator
- [X] Find a way to display all Rooms with tabs

    GAME
- [X] Create a gameroom with enough space to play and chat on the right side
- [X] Show a timer to indicate when the next match will be and the VS Panel
- [ ] Integrate chat
- [X] Possibility to invite a random player
- [ ] Create a div to show current battling players (left and right)

    CUSTOMIZE GAME
- [ ] Replace radio input for powerups and events by checkboxes

    TEMPLATES
- [x] Add {% static 'path/to/ressource' %} to all templates with {% load static %} at start
- [ ] Replace the following tags with variables: #Rank, #GamesPlayed, #Wins, #Loss, #Score, #RoomName

    PROFILE
- [ ] Add a profile list page when searching
- [ ] Fix buttons according to context
- [X] Make a chart to check games won, games lost and more

    SOCIAL
- [X] Show player context (online, offline, ingame)
- [X] Rework page
- [X] ADD another status "Waiting" , replace playing color by blue , waiting in orange
- [X] Make the chat focus last message

    LEADERBOARD
- [ ] Make better 2nd and third place
- [ ] Rework page 

    NOTIFICATION
- [X] Add a little notifcation center
- [ ] Rework notification center
- [ ] Add a tab to see friend requests

    CREATE_GAME
- [X] Fix formData being empty on chrome

    SETTINGS
- [X] Fix the second and third panel's responsive
- [X] Add a modal or a wayto inform the user that an email has been set to reset his password/email
- [X] Add a modal for account deletion with asking user password twice
- [X] Add a file input to change the persons avatar
- [X] Create a template for change email
- [X] Fix the way to change persons Avatar/Nickname
- [X] Add players default language

    CHANGE PASS/MAIL - RANDOM CODE
- [ ] Create modal to verify code for mail/password change

Reminder for Pipenv install in django:
run ```pip install --upgrade pip ``` to check location of pip
then launch ```/mnt/nfs/homes/daumis/.local/bin/pipenv install```

Reminder to check postgres:
psql db user
\dt
SELECT * FROM friends_friendrequest;

