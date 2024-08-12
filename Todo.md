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
- [ ] Put tooltips on every icon

    HOME
- [X] Create a modal for "Create GameRoom"
- [X] Add dropdown for languages (FR, EN, JP)
- [ ] Move Player search to the right side
- [ ] Add a background for "Search Game"
- [ ] Remove the "Stats Indicator" , Create a Rank indicator
- [ ] Find a way to display all Rooms with tabs

    GAME
- [X] Create a gameroom with enough space to play and chat on the right side
- [X] Show a timer to indicate when the next match will be and the VS Panel
- [ ] Integrate chat
- [X] Possibility to invite a random player

    CUSTOMIZE GAME
- [ ] Replace radio input for powerups and events by checkboxes

    TEMPLATES
- [x] Add {% static 'path/to/ressource' %} to all templates with {% load static %} at start
- [ ] Replace the following tags with variables: #Rank, #GamesPlayed, #Wins, #Loss, #Score, #RoomName

    PROFILE
- [ ] Add a profile list page when searching
- [ ] Fix buttons according to context
- [ ] Make a chart to check games won, games lost and more

    SOCIAL
- [X] Show player context (online, offline, ingame)
- [ ] Rework page

    LEADERBOARD
- [ ] Make better 2nd and third place
- [ ] Rework page 

    NOTIFICATION
- [X] Add a little notifcation center

-   CREATE_GAME
- [X] Fix formData being empty on chrome

    SETTINGS
- [X] Fix the second and third panel's responsive
- [X] Add a modal or a wayto inform the user that an email has been set to reset his password/email
- [X] Add a modal for account deletion with asking user password twice
- [X] Add a file input to change the persons avatar
- [X] Create a template for change email
- [X] Fix the way to change persons Avatar/Nickname
- [X] Add players default language

Reminder for Pipenv install in django:
run ```pip install --upgrade pip ``` to check location of pip
then launch ```/mnt/nfs/homes/daumis/.local/bin/pipenv install```

Reminder to check postgres:
psql db user
\dt
SELECT * FROM friends_friendrequest;