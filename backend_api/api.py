import flask

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

from flask_sock import Sock
from flask_socketio import SocketIO, emit
import json
import data_handling
from data_handling import application_exists #Our file for our application handling logic.
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logregister
from dotenv import load_dotenv
import os
import schema
import traceback

#Load environment variables first into memory.

#Flask-PyMongo connection(s)
app = Flask(__name__) #Create the Flask object
load_dotenv()
app.config["MONGO_URI"] = (
    f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:"
    f"{os.getenv('MONGO_PASSWORD')}@"
    f"{os.getenv('MONGO_CLUSTER')}/"
    f"{os.getenv('MONGO_DATABASE')}"
    "?retryWrites=true&w=majority"
)
mongo = PyMongo(app)
# Create indexes for app on email + company -> mongo.db.applications.create_index([("email", 1)], unique=True)

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
sock = Sock(app) #Setting up the socket object

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

#Dummy API endpoints
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/indexes', methods=['GET'])
def get_indexes():
    indexes = mongo.db.users.index_information()
    return jsonify(indexes)

#Manually adds job statuses based on company, job, email link, and status 
@app.route('/jobstatuses', methods=['POST'])
def jobstatus_manual():
    #Check if the request is JSON
    if request.is_json:
        #Get the JSON data from the request
        data = request.get_json()
        print(data)

        #Extract the parameters from the JSON
        company = data.get('company')
        date = data.get('date')
        user_email = 'name@example.com'
        company_email = data.get('company_email')
        status = data.get('status')

        #Validate that all required parameters are provided
        if not company or not date or not status or not company_email:
            return jsonify({"error": "Missing required parameters"}), 400
                
        #Obtain the JSON object from the json file
        with open('data.json') as f:
            database = json.load(f)
            f.close()
            #If the user does not exist
            if user_email not in database["users"]:
                #Add the user into a separate list of dictionaries.
                database["users"][user_email] = []
            #If there exists an application for the user with the same company and role name
            index = application_exists(company, database["users"][user_email])
            if index != -1:
                #Update the status and email link using the index for the user
                database["users"][user_email][index]["status"] = status
            #Else
            else:
                #Insert a new record into the user's list of applications (application = dictionary)
                new_application = {"date": date, "company": company, "company_email": company_email, "status": status}
                database["users"][user_email].append(new_application)
            #Dump it back into the json file
            new_json_file = json.dumps(database)
            with open('data.json', 'w') as f:
                f.write(new_json_file)
                f.close()
            return jsonify(database["users"][user_email]), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


email_list = []  # Define global variable at top of file
        
active_connections = set()

@socketio.on('connect')
def handle_connect():
    active_connections.add(request.sid)
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    active_connections.remove(request.sid)
    print(f"Client disconnected: {request.sid}")

@app.route('/emails', methods=['POST'])
def add_emails():
    global email_list
    try:
        email_data = request.get_json()
        email_list = email_data
        
        # Emit to all connected clients (Basically send the data to the frontend connecting to that)
        socketio.emit('email_update', email_data, broadcast=True)
        
        return jsonify({"message": "Emails saved and broadcast successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        #Get the JSON data from the request
        data = request.get_json()
        print(data)
                
        # Fetch the document with the email
        try:
            users_collection = mongo.db.users
            user = users_collection.find_one({"email": data.get('your_email')})
            # If no such document exists, print out invalid user email, no account associated
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Couldn't find your Personify account corresponding to your email."
                }), 404
            # Get it's password and verify against the currently entered password.
            verified = logregister.verify_password(data.get('pass'), user["password"])
            # If not successful, invalid password.
            if not verified:
                return jsonify({
                    "status": "error",
                    "message": "Invalid password, please try again."
                }), 403
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error connecting to database, check that out!"
            }), 500
        #If everything goes well at the end, successful login.
        return jsonify({"message": "Success messsage"}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/registration', methods=['POST'])
def registration():
    if request.is_json:
        #Get the JSON data from the request
        data = request.get_json()
        print(data)

        # Performing SHA-256 password hashing.
        data['pass'] = logregister.hash_password(data.get('pass'))
        # If user not present, login not successful.
        try:
            users_collection = mongo.db.users
            user = users_collection.find_one({"email": data.get('your_email')})
            if user:
                return jsonify({
                    "status": "error",
                    "message": "Account already exists, please login."
                }), 404
            #If everything goes well at the end, successful registration.
            users_collection.insert_one(schema.User(data.get('your_email'), data.get('pass')).to_dict())
        
            return jsonify({
                "status": "success",
                "message": "Registration successful"
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error connecting to database, check that out!"
            }), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    if request.is_json:
        #Get the JSON data from the request
        data = request.get_json()
        print(data)
        try:
            users_collection = mongo.db.users
            # If user not present, login not successful.
            user = users_collection.find_one({"email": data.get('your_email')})
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Couldn't find your Personify account corresponding to your email."
                }), 404
            # Check to see if the old and new passwords are the same.
            new_password_hash = logregister.hash_password(data["new_password"])
            if logregister.verify_password(data["new_password"], user["password"]):
                return jsonify({
                    "status": "error",
                    "message": "That is your current password, please enter a different one."
                }), 400
            # Hash the new password
            # Update the document to be the new password
            result = users_collection.update_one(
                {"email": data.get('your_email')},  # Find document by email
                {"$set": {"password": new_password_hash}}  # Update it's password field
            )
            if result.modified_count == 0:
                return jsonify({
                    "status": "error",
                    "message": "Failed to update password."
                }), 500
                
            return jsonify({
                "status": "success",
                "message": "Successfully changed your password"
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error connecting to database, check that out!"
            }), 500        
    else:
        return jsonify({"error": "Request must be JSON"}), 400
    
#Start the Flask app
if __name__ == '__main__':
    socketio.run(app, debug=True)