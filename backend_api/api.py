import flask

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

from flask_sock import Sock
from flask_socketio import SocketIO, emit
import json
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

# Update CORS configuration to allow requests from localhost:3000 (or your frontend port)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5500",  # Live server default port
            "http://127.0.0.1:5500"   # Localhost with IP address
        ],
        "supports_credentials": True
    }
})



# Update Socket.IO CORS configuration
socketio = SocketIO(app, cors_allowed_origins=[
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500"
])
sock = Sock(app)  # Setting up the socket object

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

#Fetch job applications based on required fields
#Fetch job applications based on required fields
@app.route('/filter', methods=['POST'])
def filter_applications():
    if request.is_json:
        data = request.get_json()
        print(data)
        
        applications_collection = mongo.db.applications
        users_collection = mongo.db.users
        query = {}
        
        # Extract user email (assuming it's sent in the request)
        user_email = data.get('user_email')
        if not user_email:
            return jsonify({"error": "User email is required"}), 400

        # Build the search query
        if 'role' in data and not any(k in data for k in ['date', 'company', 'company_email', 'status']):
            query['role'] = {'$regex': data['role'], '$options': 'i'}
            search_term = data['role']
        else:
            if 'date' in data:
                query['date'] = data['date']
            if 'company' in data:
                query['company'] = {'$regex': data['company'], '$options': 'i'}
            if 'company_email' in data:
                query['company_email'] = {'$regex': data['company_email'], '$options': 'i'}
            if 'status' in data:
                query['status'] = data['status']

            #  Constructs a single search term string by joining non-empty values from 'role', 'company', 'date', and 'status' keys in the data dictionary with spaces.
            search_term = " ".join([data.get(k, '') for k in ['role', 'company', 'date', 'status'] if data.get(k)])

        # Fetch application results
        results = list(applications_collection.find(query).limit(5))
        for result in results:
            result['_id'] = str(result['_id'])

        # Update user's recent searches
        if search_term:
            user = users_collection.find_one({"email": user_email})
            if user:
                searches = user.get("searches", [])
                searches.insert(0, search_term)
                searches = searches[:5]  # Keep only 5 most recent
                users_collection.update_one(
                    {"email": user_email},
                    {"$set": {"searches": searches}}
                )

        return jsonify({"success": True, "applications": results}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400

#Manually adds job statuses based on company, job, email link, and status 
@app.route('/jobstatuses', methods=['POST'])
def jobstatus_manual():
    if request.is_json:
        data = request.get_json()
        print(data)

        # Extract the parameters from the JSON
        fields = ('company', 'date', 'role', 'user_email', 'company_email', 'status')
        company, date, role, user_email, company_email, status = (data.get(field) for field in fields)

        # Insert the application into MongoDB
        try:
            applications_collection = mongo.db.applications
            applications_collection.update_one(
                {"user_email": user_email, "company": company, 'role': role},
                {"$set": {"date": date, "company_email": company_email, "status": status}},
                upsert=True  # Create a new document if no document matches the query
            )
            return jsonify({"success": True, "message": "Application status updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400

# New endpoint to process classified email data for job applications
@app.route('/process_application', methods=['POST'])
def process_application():
    if request.is_json:
        data = request.get_json()
        print(data)

         # Extract the parameters from the JSON
        fields = ('company', 'date', 'role', 'user_email', 'company_email', 'status')
        company, date, role, user_email, company_email, status = (data.get(field) for field in fields)

        # Insert the application into MongoDB
        try:
            applications_collection = mongo.db.applications
            
            #updates application status
            applications_collection.update_one(
                {"user_email": user_email, "company": company, "role": role},
                {"$set": {"date": date, "company_email": company_email, "status": status}},
                upsert=True  # Create a new document if no document matches the query
            )
            return jsonify({"message": "Application processed successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400

email_list = []  # Define global variable at top of file
        
active_connections = set() #Maintain a set of active connections between client and backend sockets.

#When client connects to backend socket, set up new connection.
@socketio.on('connect')
def handle_connect():
    active_connections.add(request.sid)
    print(f"Client connected: {request.sid}")

#Clear the connection whenever user logs out of the application.
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
    
#Method endpoints for login page (login, register, forgot password).

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        #Get the JSON data from the request
        data = request.get_json()
        print(data)
                
        try:
            users_collection = mongo.db.users
            # Fetch the user document corresponding the email
            user = users_collection.find_one({"email": data.get('your_email')})
            # If no such document exists, user account non existant.
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Couldn't find your Personify account corresponding to your email."
                }), 404
            # Verify the entered password against the user's current password.
            verified = logregister.verify_password(data.get('pass'), user["password"])
            # If not successful, invalid password.
            if not verified:
                return jsonify({
                    "status": "error",
                    "message": "Invalid password, please try again."
                }), 403
        except Exception as e:
            #Either an exception or a database error.
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

        # Performing client-side encryption on password using SHA-256 Hashing. 
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
            #Either exception or issues connecting to database.
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
            user = users_collection.find_one({"email": data.get('your_email')})
            # If user not present, then you have to register for a new account.
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
            # Update the document's password to be the new password
            result = users_collection.update_one(
                {"email": data.get('your_email')},  # Find document by email
                {"$set": {"password": new_password_hash}}  # Update it's password field
            )
            #If we failed to modify the document, then we failed to update password.
            if result.modified_count == 0:
                return jsonify({
                    "status": "error",
                    "message": "Failed to update password."
                }), 501
                
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