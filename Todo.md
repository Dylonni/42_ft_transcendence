    LOGIN

- [X] Create a template for "forgot password" (mail input)
- [X] Create a template for "confirm new password" (password input) -> create a show password button
- [X] Make the "show password" work
- [ ] Create Divs to load upon error codes

    NAVBAR
- [ ] Rework the navbar by adding a page to localplay
- [ ] Make the navbar show icons depending on context

    HOME
- [ ] Create a modal for "Create GameRoom"
- [ ] Add dropdown for languages (FR, EN, JP)
- [ ] Move Player search to the right side
- [ ] Add a background for "Search Game"
- [ ] Remove the "Stats Indicator" , Create a Rank indicator
- [ ] Find a way to display all Rooms with tabs

    GAME
- [ ] Create a gameroom with enough space to play and chat on the right side
- [ ] Show a timer to indicate when the next match will be and the VS Panel

    TEMPLATES
- [x] Add {% static 'path/to/ressource' %} to all templates with {% load static %} at start
- [ ] Replace the following tags with variables: #Rank, #GamesPlayed, #Wins, #Loss, #Score, #RoomName

    PROFILE
- [ ] Add a profile list page when searching
- [ ] Fix buttons according to context
- [ ] Make a chart to check games won, games lost and more

-   SOCIAL
- [ ] Show player context (online, offline, ingame)

    LEADERBOARD
- [ ] Make better 2nd and third place
- [ ] Find a way to display all ranks with tabs

    NOTIFICATION
- [X] Add a little notifcation center

    SETTINGS
- [ ] Fix the second and third panel's responsive
- [ ] Add a modal or a wayto inform the user that an email has been set to reset his password/email
- [ ] Add a modal for account deletion with asking user password twice
- [ ] Add a file input to change the persons avatar
- [X] Create a template for change email
- [ ] Fix the way to change persons Avatar/Nickname

Reminder for Pipenv install in django:
run ```pip install --upgrade pip ``` to check location of pip
then launch ```/mnt/nfs/homes/daumis/.local/bin/pipenv install```

Reminder to check postgres:
psql db user
\dt
SELECT * FROM friends_friendrequest;