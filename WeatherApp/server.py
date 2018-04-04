import os, time, os.path, psycopg2, psycopg2.extras, requests
from flask import Flask, render_template, request
#Need this for calendar widget
import datetime
#Need these lines so drop down by location will work
import sys  
#Need for json.loads
import json, ast

reload(sys)  
sys.setdefaultencoding('utf8')
#Need these lines so drop down by location will work

app = Flask(__name__)
application = app

password = False
key = "d9929daf1c0c94de0546002bbcf12c5c"

def connectToDB():
    connectionString = 'dbname=world user=weatherapp password=Password1 host=localhost'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Cannot connect to DB")
        
        
@application.route('/', methods=['GET', 'POST'])
def mainIndex(): 
    validDate = True
    validLocation = True
    now = datetime.datetime.now()
    todaysDate = now.strftime("%Y-%m-%d")
    conn = connectToDB()
    curr = conn.cursor()
            
    if request.method == 'POST':
        try:
            if request.form['weatherSearch']:
                #Grab what is in the location field
                location = request.form['locationInput']
                date = request.form['dateInput']
                print('Date: ' + date)
                if date == '':
                    #They entered an invalid date
                    print("Invalid date")
                    validDate = False
                try:
                    #Try and see if you can get anything in the city, state_id format (most will be this), format the string by delimiting by ','
                    location = location.split(',')
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
                            curr.execute("SELECT lat, lng FROM cities where zip like %s;", (wildCardedZipCode, ))
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
                        date = time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())
                        validLocation = True
                        try:
                         #Allows you to access your JSON data easily within your code. Includes built in JSON decoder
                            apiCall = "https://api.darksky.net/forecast/" + key + "/" + str(latitude) + "," + str(longitude) + "," + str(int(date)) + "?exclude=currently,minutely,hourly,alerts,flags"
                            #Request to access API
                            response = requests.get(apiCall)
                            #Creates python dictionary w/unicode from JSON weather information from API
                            weatherData = response.json()
                            print type(weatherData)
                            #Retrieves data from daily weatherData dictionary and turns it into a list (why though??)
                            d = weatherData['daily']['data'][0]
                            print d
                            print type(d)
                            print ""
                            #Turns dictionary into a list and gets rid of unicode
                            dailyData = ast.literal_eval(json.dumps(d))
                            print dailyData
                            print("Succesfully retrieved data from python dictionary")
                        except:
                            print("Call to dictionary failed")
                    else:
                        #It was not a valid entry, please reenter, try and figure out how to do this message lol
                        print("This was not a valid input.")
                        validLocation = False
                    
                except:
                    print("Error selecting information from cities.") 
        except:
            print('There was an error accessing the table ')
    try:
        curr.execute("SELECT city, state_id, zip FROM cities;")
    except:
        print("Error selecting information from cities.")
    results = curr.fetchall();
    return render_template('index.html', results=results, todaysDate=todaysDate, validDate=validDate, validLocation=validLocation)
    
    
#Start the server here
if __name__ == '__main__':
    application.run(host = os.getenv('IP', '0.0.0.0'), port = int(os.getenv('PORT', 8080)), debug = True)