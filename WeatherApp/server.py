import os, time, os.path, psycopg2, psycopg2.extras
from flask import Flask, render_template, request

app = Flask(__name__)
application = app

password = False

#def connectToDB():
#    connectionString = 'dbname=contacts user=cuser password=123abc host=localhost'
#    try:
#        return psycopg2.connect(connectionString)
#    except:
#        print("Cannot connect to DB")
        
        
@application.route('/')
def mainIndex(): 
    return render_template('index.html')
    
    
#Start the server here
if __name__ == '__main__':
    application.run(host = os.getenv('IP', '0.0.0.0'), port = int(os.getenv('PORT', 8080)), debug = True)