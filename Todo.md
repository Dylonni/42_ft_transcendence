    LOGIN

- [ ] Create a template for "forgot password" (mail input)
- [X] Create a template for "confirm password" (password input) -> create a show password button
- [X] Make the "show password" work


    HOME
- [ ] Create a modal for "Create GameRoom"
- [ ] Add dropdown for languages (FR, EN, JP)
- [ ] Move Player search to the right side
- [ ] Add a background for "Search Game"
- [ ] Remove the "Stats Indicator" , Create a Rank indicator

    TEMPLATES
- [x] Add {% static 'path/to/img' %} to all templates with {% load static %} at start
- [ ] Replace the following tags with variables: #Rank, #GamesPlayed, #Wins, #Loss, #Score, #RoomName


    Profile Page
- [ ] Add a profile list page when searching

    NOTIFICATION
- [ ] Add a little notifcation center

    SETTINGS
- [ ] Fix the second and third panel's responsive
- [ ] Add a modal or a wayto inform the user that an email has been set to reset his password/email
- [ ] Add a file input to change the persons avatar
- [X] Create a template for change email

Reminder for Pipenv install in django:
run ```pip install --upgrade pip ``` to check location of pip
then launch ```/mnt/nfs/homes/daumis/.local/bin/pipenv install```

Reminder to check postgres:
psql db user
\dt
SELECT * FROM friends_friendrequest;