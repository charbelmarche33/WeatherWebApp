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
- sudo service postgresql restart

To set the password for a user on the new DB (I already did this):
_____________________________________________________________________
- sudo sudo -u postgres psql
- ^^(postgres is superuser, instead use weatherapp, now that it is created) > psql -U weatherapp -h localhost world
- Enter a new password with "\password", then enter a password
- Running the sql file to DB: \i cities.sql
- Quit with "\q"

Logging in:
________________________________________
- sudo service postgresql restart
- psql -h localhost -d world -U weatherapp
- ******PASSWORD IS "password1"*******


password1
\i cities.sql

Git Push:
git add *
git commit -m ""
git push addressofrepository

If you are on Debian/Ubuntu, you can get all the dependencies required to build Matplotlib with:
sudo apt-get build-dep python-matplotlib



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
Dark Sky API Key: d9929daf1c0c94de0546002bbcf12c5c
__________________________________________________________________
For creating Charts
https://www.chartjs.org/


