First and foremost:
__________________________________________________
- Start a new cloud 9 project using the html template, NOT the python template
- Link it to the github repository
- Pull from the repository


To get this running do these commands in terminal:
__________________________________________________

- sudo apt-get update
- sudo apt-get install python-psycopg2
- sudo easy_install flask markdown

To start the postgreSQL server: Video here (https://www.youtube.com/watch?v=eTKzQWdw8pE)
___________________________________________________
- sudo service postgresql start (you probably can use restart since I already started it)

To set the password for a user on the new DB (I already did this):
_____________________________________________________________________
- sudo sudo -u postgres psql
- ^^(postgres is superuser, instead use weatherapp, now that it is created) > psql -U weatherapp -h localhost world
- Enter a new password with "\password", then enter a password
- Running the sql file to DB: \i cities.sql
- Quit with "\q"

Logging in:
________________________________________
- psql -U postgres -h localhost
- ******PASSWORD IS "Password1"*******







__________________________________________________________________
##################################################################
USEFUL STUFF FOR LATER
##################################################################
__________________________________________________________________
For the calender widget im working on check out this site (Set max date min date etc):
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/date
__________________________________________________________________
Setting a default date:
https://www.w3schools.com/jsref/prop_date_value.asp
__________________________________________________________________
Formatting calendar widget:
https://codepen.io/tgrant54/pen/LFblv
__________________________________________________________________



