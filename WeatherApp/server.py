import os, time, os.path, psycopg2, psycopg2.extras, requests
from flask import Flask, render_template, request, session, redirect, url_for
#Need this for calendar widget
import datetime
#Need these lines so drop down by location will work
import sys  
#Need for json.loads
import json, ast
#Need for getting rid of special characters in location output
import re 

reload(sys)  
sys.setdefaultencoding('utf8')
#Need these lines so drop down by location will work

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')
application = app

password = False
key = "d9929daf1c0c94de0546002bbcf12c5c"

def connectToDB():
    connectionString = 'dbname=world user=weatherapp password=Password1 host=localhost'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Cannot connect to DB")
        
@application.route('/signout', methods=['GET', 'POST'])
def logout():
    #This is a dummy function that the link that logs users out refers to. No page is loaded here
    #All that happens is the user is logged out and gets redirected to the main page.
    session['username'] = ''
    return redirect(url_for('mainIndex'))
        

@application.route('/', methods=['GET', 'POST'])
def mainIndex(): 
    #If the user name hasn't been created yet then set to '' otherwise someone is logged in dont
    #The try will break and make you go to the except where you set username to ''
    try:
        print('User: ' + session['username'])
    except:
        #Session ensures that the logged in status remains across tabs and clicks. It is a variable stored in the cache of the browser being used!
        #ALSO NOTE that username is used in the index file as a way to tell if anyone is logged in!
        session['username'] = ''
    
    #Starts off true, even tho noone is logged in so that when they view the log in pop up
    #they don't see an error message
    validSignUpCredentials = True
    validLogInCredentials = True
    validDate = True
    validLocation = True
    
    now = datetime.datetime.now()
    todaysDate = now.strftime("%Y-%m-%d")
    conn = connectToDB()
    curr = conn.cursor()
    lowTemp = ""
    highTemp = ""
    precip = ""
    wind = ""
    humidity = ""
    currentTemp = ""
    location = ""
    currentTempBool = ""
    todayicon = "static/images/icons/icon-umberella.png"
    if request.method == 'POST':
        try:
            if request.form['logout']:
                session['username']= ''
            #If the user hit the sumbit button on the signup form then do this
            if request.form['signup']:
                #Get the entered username and pwd from form
                username = request.form['newUsername']
                password = request.form['newPassword']
                
                try:
                    #See if these credentials match anything in the users table
                    print(curr.mogrify("SELECT * FROM users where username = %s;", (username, )))
                    curr.execute("SELECT * FROM users where username = %s;", (username, ))
                    
                    #If there are results
                    if (curr.fetchone()):
                        validSignUpCredentials = False
                    else:
                        #Set a session variable (so that the user stays logged in across multiple tabs)
                        session['username'] = username
                        query = curr.mogrify("INSERT into users (username, password) VALUES (%s,%s);", (username, password))
                        print(query)
                        curr.execute(query)
                        conn.commit()
                        curr.execute("SELECT * FROM users;")
                        res = curr.fetchall()
                        print(res)
                        
                except:
                    print("There was an error in the sign up")
             #If the user hit the Search for Weather data button do this   
            elif request.form['weatherSearch']:
                #Grab what is in the location field
                location = request.form['locationInput']
                getLocation = location
                date = request.form['dateInput']
                if date == '':
                    #They entered an invalid date
                    print("Invalid date")
                    validDate = False
                try:
                    #Try and see if you can get anything in the city, state_id format (most will be this), format the string by delimiting by ','
                    location = location.split(',')
                    #Did user enter zip code
                    isZip = False
                    #If the location string had a comma in it
                    if (len(location) > 1):
                        #Then we should check and see if they formatted the input like King George, VA and remove the white space before 'VA'
                        #The string would now be ['King George', ' VA'] we want ['King George', 'VA']
                        if (location[1][0] == ' '):
                            #If there is white space at the start of the string, splice it off
                            location[1] = location[1][1:]
                        #Run the query
                        print(curr.mogrify("SELECT lat, lng FROM cities where city=%s and (state_id=%s or state_name=%s);", (location[0], location[1], location[1])))
                        curr.execute("SELECT lat, lng FROM cities where city=%s and (state_id=%s or state_name=%s);", (location[0], location[1], location[1]))
                    else:
                        #Then user probably entered just a zip code
                        if (len(location) == 5):
                            #Necessary to get a zip for the ones that have many zips!
                            wildCardedZipCode = '%'+location[0]+'%'
                            print(curr.mogrify("SELECT lat, lng FROM cities where zip like %s;", (wildCardedZipCode, )))
                            curr.execute("SELECT lat, lng, city, state FROM cities where zip like %s;", (wildCardedZipCode, ))
                            #It is a zip code
                            isZip = True
                        else:
                            #It was not a valid entry, please reenter, try and figure out how to do this message lol
                            print("This was not a valid zip cause wrong number of numbers, who taught you to count")
                            validLocation = False
                    #If there is a result, then it was a valid entry
                    latLong = curr.fetchone()
                    if latLong:
                        print(latLong)
                        latitude = latLong[0]
                        longitude = latLong[1]
                        if (isZip):
                            getLocation = latLong[2] + ', ' + latLong[3]
                        
                        #Gets the unix time
                        unixDate = time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())
                        validLocation = True
                        try:
                         #Allows you to access your JSON data easily within your code. Includes built in JSON decoder
                            apiCall = "https://api.darksky.net/forecast/" + key + "/" + str(latitude) + "," + str(longitude) + "," + str(int(unixDate)) + "?exclude=currently,minutely,hourly,alerts,flags"
                            #Request to access API
                            response = requests.get(apiCall)
                            #Creates python dictionary w/unicode from JSON weather information from API
                            weatherData = response.json()
                            #Retrieves data from daily weatherData dictionary and turns it into a list (why though??)
                            dailyData = weatherData['daily']['data'][0]
                            #Pairs a weather picture with the weather icon from DarkSky. (Haven't found a good placeholder before a search is made)
                            wicon = dailyData['icon']
                            print(wicon + ' is wicon')
                            lowTemp = dailyData['temperatureLow']                   #Degrees Farenheit
                            highTemp = dailyData['temperatureHigh']                 #Degrees Farenheit
                            #averageTemp = []
                            precip = dailyData['precipProbability'] * 100           # percentage
                            wind = dailyData['windSpeed']                           # miles/hour
                            humidity = dailyData['humidity'] * 100                  # percentage
                            print("Low Temperature: " + str(lowTemp))
                            print("High Temperature: " + str(highTemp))
                            print("Precipitation: " + str(precip) + "%")
                            print("Wind Speed: " + str(wind) + " mph")
                            print("Humidity: " + str(humidity) + "%")
                            
                            if wicon == "clear-day":
                                todayicon = "static/images/icons/icon-2.svg"
                            if wicon == "clear-night":
                                todayicon = ""
                            if wicon == "rain":
                                todayicon = "static/images/icons/icon-10.svg"
                            if wicon == "sleet":
                                todayicon = "static/images/icons/icon-10.svg"
                            if wicon == "snow":
                                todayicon = "static/images/icons/icon-14.svg"
                            if wicon == "hail":
                                todayicon =  "static/images/icons/icon-14.svg"
                            if wicon == "wind":
                                todayicon = "static/images/icons/icon-wind.png"
                            if wicon == "fog":
                                todayicon = "static/images/icons/icon-7.svg"
                            if wicon == "cloudy":
                                todayicon = "static/images/icons/icon-5.svg"
                            if wicon == "partly-cloudy-day":
                                todayicon = "static/images/icons/icon-6.svg"
                            if wicon == "partly-cloudy-night":
                                todayicon = ""
                            if wicon == "thunderstorm":
                                todayicon = "static/images/icons/icon-11.svg"
                            if wicon == "tornado":
                                todayicon = "static/images/icons/icon-8.svg"
                        except:
                            print("Call to dictionary failed")
                    else:
                        #It was not a valid entry, please reenter, try and figure out how to do this message lol
                        print("This was not a valid input.")
                        validLocation = False
                except:
                    print("Error selecting information from cities.") 
            #If the user hit the submit button on the login form then do this
        except:
            #This is the sign in. This is here because there is a weird thing with having two models and using request.form that makes that 
            #throw an error when I try and do it in the first if in the try. As a result I put the log in down here so that it works out.
            #any questions ask me (charbel) and I can explain better in person
            
            
            #Get the entered username and pwd from form
            username = request.form['username']
            password = request.form['password']
            
            #See if these credentials match anything in the users table
            print(curr.mogrify("SELECT * FROM users where username = %s and password = %s;", (username, password)))
            curr.execute("SELECT * FROM users where username = %s and password = %s;", (username, password))
            #If there are results
            if (curr.fetchone()):
                #Set a session variable (so that the user stays logged in across multiple tabs)
                session['username'] = username
            else:
                validLogInCredentials = False
    try:
        curr.execute("SELECT city, state_id, zip FROM cities;")
    except:
        print("Error selecting information from cities.")
    results = curr.fetchall()
    return render_template('index.html', username=session['username'], validSignUpCredentials=validSignUpCredentials, validLogInCredentials=validLogInCredentials, results=results, todaysDate=todaysDate, lowTemp=lowTemp, highTemp=highTemp, precip=precip, wind=wind, humidity=humidity, validDate=validDate, validLocation=validLocation)
    
    
#Start the server here
if __name__ == '__main__':
    application.run(host = os.getenv('IP', '0.0.0.0'), port = int(os.getenv('PORT', 8080)), debug = True)