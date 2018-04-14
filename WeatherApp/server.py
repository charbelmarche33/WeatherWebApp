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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt # Do not do this prior to calling use()
import matplotlib.pyplot as plt1
import matplotlib.pyplot as plt2
import matplotlib.pyplot as plt3
import matplotlib.pyplot as plt4
import numpy as np
import Image

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
        
@application.route('/pastsearches', methods=['GET', 'POST'])
def pastSearches():
    if(session['username'] == ''):
        #User is not logged in, redirect to main page
        return redirect(url_for('mainIndex'))
    conn = connectToDB()
    curr = conn.cursor()
    print(curr.mogrify("SELECT * FROM pastsearches where username = %s;", (session['username'], )))
    curr.execute("SELECT * FROM pastsearches where username = %s;", (session['username'], ))
    results = curr.fetchall()
    results.reverse()
    return render_template('pastsearches.html', username=session['username'], results=results)
    
    
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
        
    #I put this stupid if statement here just so i can hide all this stuff
    if (True):
        #Starts off true, even tho noone is logged in so that when they view the log in pop up
        #they don't see an error message
        validSignUpCredentials = True
        validLogInCredentials = True
        validDate = True
        validLocation = True
        isZip = True
        
        years = np.arange(0,10,5)
        weekdayName = ""
        totalDates = ""
        totalDates1 = ""
        totalDates2 = ""
        totalDates3 = ""
        totalDates4 = ""
        now = datetime.datetime.now()
        todaysDate = now.strftime("%Y-%m-%d")
        TodaysDate = time.mktime(datetime.datetime.strptime(todaysDate, "%Y-%m-%d").timetuple())
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
        date = ""
        unixDate = ""
        getLocation= ""
        wicon = ""
        todayicon = "static/images/icons/icon-umberella.png"
        precipType = ""
        average_temperature = 0
        average_temperature1 = 0
        average_temperature2 = 0
        average_temperature3 = 0
        average_temperature4 = 0
        totalTemp = 0
        avg = 0
        average = 0
        timestr = ""
        timestr1 = ""
        timestr2 = ""
        timestr3 = ""
        timestr4 = ""
        plotFred= False
        plotCharlottesville = False
        plotHonolulu = False
        plotRichmond = False
    if request.method == 'POST':
        print("Here in main in post")
        try:
            print("Here in main in try")
            try:
                if request.form['signup']:
                    print("Here in main in sign up")
                    #Get the entered username and pwd from form
                    username = request.form['newUsername']
                    password = request.form['newPassword']
                    print('Here')
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
            except:
                print("Here in weather search")
                if request.form['weatherSearch']:
                    #Grab what is in the location field
                    print("Here in if of weather search date is " + date)
                    location = request.form['locationInput']
                    getLocation = location
                    date = request.form['dateInput']
            
                    if date == '':
                        #They entered an invalid date
                        print("Invalid date")
                        validDate = False
                    else:
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
                                print(location[0])
                                if (len(location[0]) == 5):
                                    print("Here in main in zip")
                                    #Necessary to get a zip for the ones that have many zips!
                                    wildCardedZipCode = '%'+location[0]+'%'
                                    print(curr.mogrify("SELECT lat, lng FROM cities where zip like %s;", (wildCardedZipCode, )))
                                    curr.execute("SELECT lat, lng, city, state_id FROM cities where zip like %s;", (wildCardedZipCode, ))
                                    print("Here in main after execute")
                                    #It is a zip code
                                    isZip = True
                                else:
                                    #It was not a valid entry, please reenter, try and figure out how to do this message lol
                                    print("This was not a valid zip cause wrong number of numbers, who taught you to count")
                                    getLocation = ''
                                    validLocation = False
                                    
                            #If there is a result, then it was a valid entry
                            latLong = curr.fetchone()
                            if latLong:
                                print(latLong)
                                if (isZip):
                                    #Did this so that if zip dylons tables dont cause crashes
                                    location = latLong[2] + ',' + latLong[3]
                                    location = location.split(',')
                                    getLocation = latLong[2] + ', ' + latLong[3]
                                    print("Its zip")
                                latitude = latLong[0]
                                longitude = latLong[1]
                                print(latLong)
                                latitude = latLong[0]
                                longitude = latLong[1]
                                date = time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())
                                unixDate = date
                                validLocation = True
                                #if date equals todaysdate statement
                                #how to get u code back
                                TodaysDate = time.mktime(datetime.datetime.strptime(todaysDate, "%Y-%m-%d").timetuple())
                                # Returns average temperature for each half decade that the system has information about at the given location.
                                c = 0
                                count = 0
                                count1 = 0
                                count2 = 0
                                count3 = 0
                                count4 = 0
                                oneYear = 31536000
                                oneDay = 86400
                                # Gets a range of years; Starts at 5 years, increments by 5 years and ends by 30 years
                                years = np.arange(5*oneYear,30*oneYear,5*oneYear+oneDay)
                                years1 = np.arange(5*oneYear,30*oneYear,5*oneYear+oneDay)
                                years2 = np.arange(5*oneYear,30*oneYear,5*oneYear+oneDay)
                                years3 = np.arange(5*oneYear,30*oneYear,5*oneYear+oneDay)
                                years4 = np.arange(5*oneYear,30*oneYear,5*oneYear+oneDay)
                                average_temperature = np.empty(years.size)
                                average_temperature1 = np.empty(years1.size)
                                average_temperature2 = np.empty(years2.size)
                                average_temperature3 = np.empty(years3.size)
                                average_temperature4 = np.empty(years4.size)
                                totalDates = np.array([])
                                totalDates1 = np.array([])
                                totalDates2 = np.array([])
                                totalDates3 = np.array([])
                                totalDates4 = np.array([])
                                d = ""
                                
                                #Fredericksburg, VA
                                while plotFred:
                                    latitude1 = 38.30318370
                                    longitude1 = -77.46053990
                                    for i in years1:
                                    
                                        # Loop that returns the correct date that corresponds with the 
                                        # day the user chooses. There are 5 dates. All are 5 years apart.
                                        # The dates are in the past and have historical averages for temperature.
                                        # The dates begin 5 years before the users chosen date and continue to 
                                        # decrease every five years
                                        newDate1 = date
                                        if newDate1 - i <= newDate1 - (15*oneYear):
                                            newDate1 = newDate1 - i - oneDay - oneDay
                                        else:
                                            newDate1 = newDate1 - i - oneDay
                                          
                                        a1 = "https://api.darksky.net/forecast/" + key + "/" + str(latitude1) + "," + str(longitude1) + "," + str(int(newDate1)) + "?exclude=minutely,hourly,alerts,flags"
                                        r1 = requests.get(a1)
                                        data1 = r1.json()
                                        current1 = data1['currently']
                                        c1 = current1['temperature']
                                        # Gets all the dates, converts to Y-m-d, and stores them in an array
                                        d1 = datetime.datetime.fromtimestamp(newDate1)
                                        d1 = d1.date()
                                        totalDates1 = np.append(totalDates1, d1)
                                        # Gets average temp at each year and stores value in an array
                                        average_temperature1[count1] = c1
                                        count1+=1
                                    len_average_temperature1 = np.arange(len(average_temperature1))
                                    plt1.cla()   # Clear axis
                                    plt1.clf()   # Clear figure
                                    #Plots bar graph for average temp for each half decade of given location
                                    plt1.bar(len_average_temperature1, average_temperature1, align="center", alpha=0.5)
                                    plt1.xticks(len_average_temperature1, totalDates1)
                                    plt1.xlabel("Date (Y-M-D)", fontsize=10)
                                    plt1.ylabel("Temperature in Fahrenheit", fontsize=10)
                                    plt1.title("Temperature for Each Half Decade in Fredericksburg, VA", fontsize=12)
                                    #Creates an image file with the timestamp in the name so the image is always refreshed in window
                                    timestr1 = now.strftime("%Y%m%d-%H%M%S")
                                    plt1.savefig('static/images/'+timestr1+"moretime"'.png')
                                    plotFred = False
                                    
                                # Charlottesville, VA    
                                while plotCharlottesville:
                                    latitude2 = 38.02930590
                                    longitude2 = -78.47667810
                                    for k in years2:
                                    
                                        # Loop that returns the correct date that corresponds with the 
                                        # day the user chooses. There are 5 dates. All are 5 years apart.
                                        # The dates are in the past and have historical averages for temperature.
                                        # The dates begin 5 years before the users chosen date and continue to 
                                        # decrease every five years
                                        newDate2 = date
                                        if newDate2 - k <= newDate2 - (15*oneYear):
                                            newDate2 = newDate2 - k - oneDay - oneDay
                                        else:
                                            newDate2 = newDate2 - k - oneDay
                                          
                                    
                                        a2 = "https://api.darksky.net/forecast/" + key + "/" + str(latitude2) + "," + str(longitude2) + "," + str(int(newDate2)) + "?exclude=minutely,hourly,alerts,flags"
                                        r2 = requests.get(a2)
                                        data2 = r2.json()
                                        current2 = data2['currently']
                                        c2 = current2['temperature']
                                        # Gets all the dates, converts to Y-m-d, and stores them in an array
                                        d2 = datetime.datetime.fromtimestamp(newDate2)
                                        d2 = d2.date()
                                        totalDates2 = np.append(totalDates2, d2)
                                        # Gets average temp at each year and stores value in an array
                                        average_temperature2[count2] = c2
                                        count2+=1
                                    len_average_temperature2 = np.arange(len(average_temperature2))
                                    plt2.cla()   # Clear axis
                                    plt2.clf()   # Clear figure
                                    #Plots bar graph for average temp for each half decade of given location
                                    plt2.bar(len_average_temperature2, average_temperature2, align="center", alpha=0.5)
                                    plt2.xticks(len_average_temperature2, totalDates2)
                                    plt2.xlabel("Date (Y-M-D)", fontsize=10)
                                    plt2.ylabel("Temperature in Fahrenheit", fontsize=10)
                                    plt2.title("Temperature for Each Half Decade in Charlottesville, VA", fontsize=12)
                                    #Creates an image file with the timestamp in the name so the image is always refreshed in window
                                    timestr2 = now.strftime("%Y%m%d-%H%M%S")
                                    plt2.savefig('static/images/'+timestr2+"moretime2"'.png')
                                    plotCharlottesville = False
                                      
                                # Honolulu, HI   
                                while plotHonolulu:
                                    latitude3 = 21.30694440
                                    longitude3 = -157.85833330
                                    for h in years3:
                                    
                                        # Loop that returns the correct date that corresponds with the 
                                        # day the user chooses. There are 5 dates. All are 5 years apart.
                                        # The dates are in the past and have historical averages for temperature.
                                        # The dates begin 5 years before the users chosen date and continue to 
                                        # decrease every five years
                                        newDate3 = date
                                        if newDate3 - h <= newDate3 - (15*oneYear):
                                            newDate3 = newDate3 - h - oneDay - oneDay
                                        else:
                                            newDate3 = newDate3 - h - oneDay
                                          
                                    
                                        a3 = "https://api.darksky.net/forecast/" + key + "/" + str(latitude3) + "," + str(longitude3) + "," + str(int(newDate3)) + "?exclude=minutely,hourly,alerts,flags"
                                        r3 = requests.get(a3)
                                        data3 = r3.json()
                                        current3 = data3['currently']
                                        c3 = current3['temperature']
                                        # Gets all the dates, converts to Y-m-d, and stores them in an array
                                        d3 = datetime.datetime.fromtimestamp(newDate3)
                                        d3 = d3.date()
                                        totalDates3 = np.append(totalDates3, d3)
                                        # Gets average temp at each year and stores value in an array
                                        average_temperature3[count3] = c3
                                        count3+=1
                                    len_average_temperature3 = np.arange(len(average_temperature3))
                                    plt3.cla()   # Clear axis
                                    plt3.clf()   # Clear figure
                                    #Plots bar graph for average temp for each half decade of given location
                                    plt3.bar(len_average_temperature3, average_temperature3, align="center", alpha=0.5)
                                    plt3.xticks(len_average_temperature3, totalDates3)
                                    plt3.xlabel("Date (Y-M-D)", fontsize=10)
                                    plt3.ylabel("Temperature in Fahrenheit", fontsize=10)
                                    plt3.title("Temperature for Each Half Decade in Charlottesville, VA", fontsize=12)
                                    #Creates an image file with the timestamp in the name so the image is always refreshed in window
                                    timestr3 = now.strftime("%Y%m%d-%H%M%S")
                                    plt3.savefig('static/images/'+timestr3+"moretime3"'.png')
                                    plotHonolulu = False
                                
                                # Richmond, VA
                                while plotRichmond:
                                    latitude4 = 37.55375750
                                    longitude4 = -77.46026170
                                    for j in years4:
                                    
                                        # Loop that returns the correct date that corresponds with the 
                                        # day the user chooses. There are 5 dates. All are 5 years apart.
                                        # The dates are in the past and have historical averages for temperature.
                                        # The dates begin 5 years before the users chosen date and continue to 
                                        # decrease every five years
                                        newDate4 = date
                                        if newDate4 - j <= newDate4 - (15*oneYear):
                                            newDate4 = newDate4 - j - oneDay - oneDay
                                        else:
                                            newDate4 = newDate4 - j - oneDay
                                          
                                    
                                        a4 = "https://api.darksky.net/forecast/" + key + "/" + str(latitude4) + "," + str(longitude4) + "," + str(int(newDate4)) + "?exclude=minutely,hourly,alerts,flags"
                                        r4 = requests.get(a4)
                                        data4 = r4.json()
                                        current4 = data4['currently']
                                        c4 = current4['temperature']
                                        # Gets all the dates, converts to Y-m-d, and stores them in an array
                                        d4 = datetime.datetime.fromtimestamp(newDate4)
                                        d4 = d4.date()
                                        totalDates4 = np.append(totalDates4, d4)
                                        # Gets average temp at each year and stores value in an array
                                        average_temperature4[count4] = c4
                                        count4+=1
                                    len_average_temperature4 = np.arange(len(average_temperature4))
                                    plt4.cla()   # Clear axis
                                    plt4.clf()   # Clear figure
                                    #Plots bar graph for average temp for each half decade of given location
                                    plt4.bar(len_average_temperature4, average_temperature4, align="center", alpha=0.5)
                                    plt4.xticks(len_average_temperature4, totalDates4)
                                    plt4.xlabel("Date (Y-M-D)", fontsize=10)
                                    plt4.ylabel("Temperature in Fahrenheit", fontsize=10)
                                    plt4.title("Temperature for Each Half Decade in Charlottesville, VA", fontsize=12)
                                    #Creates an image file with the timestamp in the name so the image is always refreshed in window
                                    timestr4 = now.strftime("%Y%m%d-%H%M%S")
                                    plt4.savefig('static/images/'+timestr4+"moretime4"'.png')
                                    plotRichmond = False
                                        
                                # Location user chooses
                                for y in years:
                                    
                                    # Loop that returns the correct date that corresponds with the 
                                    # day the user chooses. There are 5 dates. All are 5 years apart.
                                    # The dates are in the past and have historical averages for temperature.
                                    # The dates begin 5 years before the users chosen date and continue to 
                                    # decrease every five years
                                    newDate = date
                                    if newDate - y <= newDate - (15*oneYear):
                                        newDate = newDate - y - oneDay - oneDay
                                    else:
                                        newDate = newDate - y - oneDay
                                      
                                
                                    a = "https://api.darksky.net/forecast/" + key + "/" + str(latitude) + "," + str(longitude) + "," + str(int(newDate)) + "?exclude=minutely,hourly,alerts,flags"
                                    r = requests.get(a)
                                    data = r.json()
                                    current = data['currently']
                                    c = current['temperature']
                                    # Gets all the dates, converts to Y-m-d, and stores them in an array
                                    d = datetime.datetime.fromtimestamp(newDate)
                                    d = d.date()
                                    totalDates = np.append(totalDates, d)
                                    # Gets average temp at each year and stores value in an array
                                    average_temperature[count] = c
                                    # Gets total of temperatures in graph
                                    totalTemp += c
                                    # Counter for average_temperature array
                                    count+=1
                                # Gets average temperature for graph as float
                                avg = totalTemp/5
                                # Converts avg to int
                                average = int(avg)
                                # Gets temperatures in graph in chronological order
                                new_average_temperature = average_temperature[np.array([4, 3, 2, 1, 0])]
                                # Gets dates in graph in chronological order
                                new_totalDates = totalDates[np.array([4, 3, 2, 1, 0])]
                                # Gets length of average_temperature
                                len_average_temperature = np.arange(len(average_temperature))
                                plt.cla()   # Clear axis
                                plt.clf()   # Clear figure
                                #Plots bar graph for average temp for each half decade of given location
                                plt.bar(len_average_temperature, new_average_temperature, align="center", color = "dodgerblue", edgecolor = "dodgerblue", alpha=0.5)
                                plt.xticks(len_average_temperature, new_totalDates)
                                plt.xlabel("Date (Y-M-D)", fontsize=10)
                                plt.ylabel("Temperature in Fahrenheit", fontsize=10)
                                plt.title("Temperature for Each Half Decade in " + str(location[0]) + ", " + str(location[1]), fontsize=12)
                                #Creates an image file with the timestamp in the name so the image is always refreshed in window
                                timestr = now.strftime("%Y%m%d-%H%M%S")
                                plt.savefig('static/images/'+timestr+'.png')
                                # If within next seven days give current 
                                if date <= (TodaysDate + (86400*7)):
                                    try:
                                        #Allows you to access your JSON data easily within your code. Includes built in JSON decoder
                                        apiCall = "https://api.darksky.net/forecast/" + key + "/" + str(latitude) + "," + str(longitude) + "," + str(int(date)) + "?exclude=minutely,hourly,alerts,flags"
                                        #Request to access API
                                        response = requests.get(apiCall)
                                        #Creates python dictionary from JSON weather information from API
                                        weatherData = response.json()
                                        #Set date equal to todays date and change format
                                        date = datetime.datetime.fromtimestamp(date)
                                        date = date.date()
                                        weekdayName = date.strftime("%A")
                                        #Daily data information
                                        dailyData = weatherData['daily']['data'][0]
                                        #Currently data information
                                        currentData = weatherData['currently']
                                        currentTemp = currentData['temperature']
                                        lowTemp = dailyData['temperatureLow']                   #Degrees Farenheit
                                        highTemp = dailyData['temperatureHigh']                 #Degrees Farenheit
                                        precip = dailyData['precipProbability'] * 100           # percentage
                                        wind = dailyData['windSpeed']                           # miles/hour
                                        humidity = dailyData['humidity'] * 100                  # percentage
                                        wicon = dailyData['icon']
                                                
                                        currentTempBool = bool(currentTemp)
                                                                        
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
                                        print("Call to api failed in next 7 days")
                                else:
                                    try:
                                        #Allows you to access your JSON data easily within your code. Includes built in JSON decoder
                                        apiCall = "https://api.darksky.net/forecast/" + key + "/" + str(latitude) + "," + str(longitude) + "," + str(int(date)) + "?exclude=minutely,hourly,alerts,flags"
                                        #Request to access API
                                        response = requests.get(apiCall)
                                        #Creates python dictionary from JSON weather information from API
                                        weatherData = response.json()
                                        #Set date equal to todays date and change format
                                        date = datetime.datetime.fromtimestamp(date)
                                        date = date.date()
                                        weekdayName = date.strftime("%A")
                                        #print(weatherData)
                                        #Daily data information
                                        dailyData = weatherData['daily']['data'][0]
                                        #Currently data information
                                        currentData = weatherData['currently']
                                        #Retrieving a current temperature
                                        currentTemp = currentData['temperature']
        
                                        lowTemp = dailyData['temperatureLow']                   #Degrees Farenheit
                                        highTemp = dailyData['temperatureHigh']                 #Degrees Farenheit
                                        wicon = dailyData['icon']
                                        precipType = dailyData['precipType']        
                                        currentTempBool = bool(currentTemp)
                                                                        
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
                                        print("Call to api failed in next 7 days.")
                            else:
                                #It was not a valid entry, please reenter, try and figure out how to do this message lol
                                print("This was not a valid input.")
                                validLocation = False
                        except:
                            print("Error selecting information from cities.") 
                            getLocation = ''
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
        getLocation = ''
    results = curr.fetchall()
    
    #Return location as a string and replaces extra characters 
    if (isZip == False and getLocation != ''):
        getLocation = ast.literal_eval(json.dumps(location))
        getLocation = str(getLocation)
        getLocation = getLocation.translate(None, '\'[!@#$]')
        getLocation = getLocation.replace("",'')
        
    #This is going to add to the past searches
    if (session['username'] != '' and getLocation != '' and validLocation and validDate):
        print(getLocation)
        print(date)
        print(session['username'])
        query = curr.mogrify("INSERT into pastsearches (username, locationSearched, dateSearched) VALUES (%s,%s,%s);", (session['username'], getLocation, date))
        print(query)
        curr.execute(query)
        conn.commit()
        curr.execute("SELECT * FROM pastsearches;")
        res = curr.fetchall()
        print(res)
    return render_template('index.html', username=session['username'], validSignUpCredentials=validSignUpCredentials, 
                                        validLogInCredentials=validLogInCredentials, results=results, date=date, unixDate = unixDate, 
                                        todaysDate=todaysDate, TodaysDate=TodaysDate, weekdayName=weekdayName, average_temperature=average_temperature, lowTemp=lowTemp, 
                                        highTemp=highTemp, precip=precip, precipType=precipType, currentTemp=currentTemp, wind=wind, humidity=humidity, 
                                        getLocation=getLocation, todayicon=todayicon, wicon=wicon, validDate=validDate, validLocation=validLocation, 
                                        currentTempBool=currentTempBool, timestr=timestr, timestr1=timestr1, timestr2=timestr2, timestr3=timestr3, timestr4=timestr4, average=average)
    
    
#Start the server here
if __name__ == '__main__':
    application.run(host = os.getenv('IP', '0.0.0.0'), port = int(os.getenv('PORT', 8080)), debug = True)