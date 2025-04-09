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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from botocore.exceptions import BotoCoreError, ClientError

#Load environment variables first into memory.
load_dotenv()
#Flask-PyMongo connection(s)
app = Flask(__name__) #Create the Flask object
app.config["MONGO_URI"] = (
    f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:"
    f"{os.getenv('MONGO_PASSWORD')}@"
    f"{os.getenv('MONGO_CLUSTER')}/"
    f"{os.getenv('MONGO_DATABASE')}"
    "?retryWrites=true&w=majority"
)
mongo = PyMongo(app)
# Create indexes for app on email + company -> mongo.db.applications.create_index([("email", 1)], unique=True)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials = True)  # Allow requests from your frontend
socketio = SocketIO(app, cors_allowed_origins="*")
sock = Sock(app) #Setting up the socket object

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = flask.make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://127.0.0.1:5500")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

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
@app.route('/filter', methods=['POST'])
def filter_applications():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    print(data)
    
    applications_collection = mongo.db.applications
    users_collection = mongo.db.users
    
    # Require user_email
    user_email = data.get('user_email')
    if not user_email:
        return jsonify({"error": "User email is required"}), 400

    # Restrict to recent search to user's applications
    query = {"user_email": user_email}  
    
    # Build the search query
    search_term = {}
    if 'role' in data and not any(k in data for k in ['date', 'company', 'company_email', 'status']):
        query['role'] = {'$regex': data['role'], '$options': 'i'}
        search_term['role'] = data['role']
    else:
        if 'role' in data:
            query['role'] = {'$regex': data['role'], '$options': 'i'}
            search_term['role'] = data['role']
        if 'date' in data:
            query['date'] = data['date']
            search_term['date'] = data['date']
        if 'company' in data:
            query['company'] = {'$regex': data['company'], '$options': 'i'}
            search_term['company'] = data['company']
        if 'company_email' in data:
            query['company_email'] = {'$regex': data['company_email'], '$options': 'i'}
            search_term['company_email'] = data['company_email']
        if 'status' in data:
            query['status'] = data['status']
            search_term['status'] = data['status']

    try:
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

        return jsonify({
            "success": True,
            "message": "Applications retrieved successfully",
            "applications": results
        }), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/addquestion', methods=['POST'])
def add_question():
    if request.is_json:
        data = request.get_json()
        print(data)
        try:
            # Refer to questions collection from mongodb database
            questions_collection = mongo.db.questions

            # Check if the question already exists in the collection
            existing_question = questions_collection.find_one({"question": data.get("question")})
            if existing_question:
                return jsonify({
                    "status": "error",
                    "message": "The question already exists, please ask another question."
                }), 400

            # Add the question to the collection using Question Schema
            # Ivan: Train a model to generate the answer to this question (for automation).
            new_question = schema.Question(
                question=data.get("question"),
                answer="Thank you for answering this question, we will come back to you at a later time."
            ).to_dict()
            questions_collection.insert_one(new_question)

            # Return a success message
            return jsonify({
                "status": "success",
                "message": "Question added successfully"
            }), 200
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/new_question', methods=['POST'])
def new_question():
    try:
        # Get the new question from the request
        question = request.json

        # Emit the question to the frontend via WebSocket
        socketio.emit('new_question', question)
        
        return jsonify({"success": True, "message": "Question emitted to frontend."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


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
    
# Function to retrieve the secrets from AWS Secrets Manager for securely contacting me.
def get_email_secret():
    try:
        client = boto3.client(
            "secretsmanager",
            region_name="us-east-1",
            aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        response = client.get_secret_value(
            SecretId="arn:aws:secretsmanager:us-east-1:412381777713:secret:Email_Password-uQRzUF",
            VersionStage="AWSCURRENT",
        )
        return json.loads(response["SecretString"])
    except (BotoCoreError, ClientError) as error:
        print(f"Error retrieving secret: {error}")
        raise error

@app.route('/send_email', methods=['POST'])
def send_email():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")

    try:
        secret = get_email_secret()
        email_password = secret["PASSWORD"]

        # Set up the email
        msg = MIMEMultipart()
        msg["From"] = name
        msg["Reply-To"] = email
        msg["To"] = "nikhilsai.munagala@gmail.com"
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        # Send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            #Authenticate to the SMTP server first
            server.login("nikhilsai.munagala@gmail.com", email_password)
            #Before sending the email
            server.sendmail(email, "nikhilsai.munagala@gmail.com", msg.as_string())

        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500
    
#Start the Flask app
if __name__ == '__main__':
    socketio.run(app, debug=True)