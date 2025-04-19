import flask

from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, set_access_cookies, unset_jwt_cookies, JWTManager
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
import handling

#Load environment variables first into memory.
load_dotenv()
#Flask-PyMongo connection(s)
app = Flask(__name__) #Create the Flask object
app.config["MONGO_URI"] = (
    f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:"
    f"{os.getenv('MONGO_PASSWORD')}@"
    f"{os.getenv('MONGO_CLUSTER')}/"
    f"{os.getenv('MONGO_DATABASE')}"
    "?retryWrites=true&w=majority&ssl=true"
)
mongo = PyMongo(app)

# Configure JWT token configuration management
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")  # Fetch the secret key from environment variables
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Use cookies to store JWT
app.config["JWT_COOKIE_SECURE"] = True  # Use secure cookies (HTTPS only)
app.config["JWT_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access to cookies
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"  # Path for the access token cookie
jwt = JWTManager(app)

# Create indexes for app on email + company -> mongo.db.applications.create_index([("email", 1)], unique=True)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials = True)  # Allow requests from your frontend
socketio = SocketIO(app, cors_allowed_origins="*")
sock = Sock(app) #Setting up the socket object

# Method helps during the frontend-rest api handshake, allowing origin to access REST API, allowing GET, POST, and Options request.
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = flask.make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://127.0.0.1:5500")
        #List the methods that the origin is allowed to make.
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
        # Get the JSON data from the request
        data = request.get_json()
        print(data)

        try:
            users_collection = mongo.db.users
            # Fetch the user document corresponding to the email
            user = users_collection.find_one({"email": data.get('your_email')})
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Couldn't find your Personify account corresponding to your email."
                }), 404
            
            # Verify the entered password against the hashed password in the database
            entered_password = data.get('pass')
            hashed_password = user["password"]
            verified = logregister.verify_password(entered_password, hashed_password)
            if not verified:
                return jsonify({
                    "status": "error",
                    "message": "Invalid password, please try again."
                }), 403
            
            # Generate a JWT token upon successful login
            access_token = create_access_token(identity=user["email"])
            response = make_response(jsonify({
                "status": "success",
                "message": "Login successful"
            }), 200)
            set_access_cookies(response, access_token)
            return response
        
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An error occurred during login."
            }), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400
    
@app.route('/registration', methods=['POST'])
def registration():
    if request.is_json:
        # Get the JSON data from the request
        data = request.get_json()
        print(data)

        try:
            users_collection = mongo.db.users
            # Check if the user already exists
            user = users_collection.find_one({"email": data.get('your_email')})
            if user:
                return jsonify({
                    "status": "error",
                    "message": "Account already exists, please login."
                }), 404
            
            # Create a new User profile
            original_password = data['pass']
            #Hash the password to store in database.
            hashed_password = logregister.hash_password(original_password)
            #Create a new user object.
            new_user = schema.User(
                email=data.get('your_email'),
                password=hashed_password,
                original_password=original_password,
                encrypted=False
            )
            
            # Save the user to the database
            users_collection.insert_one(new_user.to_dict())
            
            # Generate a JWT token for the newly registered user
            access_token = create_access_token(identity=data.get('your_email'))
            response = make_response(jsonify({
                "status": "success",
                "message": "Registration successful"
            }), 200)
            set_access_cookies(response, access_token)
            return response
        
        except Exception as e:
            print(f"Error during registration: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An error occurred during registration."
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
            # Create a schema.User object from the user document
            user_obj = schema.User.from_mongo_document(user)
            print(user_obj.to_dict())
            
            # Make an AWS KMS call to decrypt User's encrypted_dek
            # Retrieve access_key and secret_access_key from the .env file
            try:
                access_key = os.getenv("ACCESS_KEY_ID")
                secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            except ValueError as e:
                return jsonify({
                    "status": "error",
                    "message": f"AWS credentials are missing in the environment variables."
                }), 500
            decrypted_dek = handling.decrypt_dek(user_obj._encrypted_key, access_key, secret_access_key)
            user_obj._key = decrypted_dek
            # Encrypt the new password using the User's encrypt method
            encrypted_password = user_obj._encrypt(data["new_password"])
            user_obj._key = '' #Discard after encryption for security purposes.
            # Update the document's encrypted password field
            result = users_collection.update_one(
                {"email": data.get('your_email')},  # Find document by email
                {"$set": {"password": new_password_hash, "original_password": encrypted_password}}  # Update fields
            )
            #If we failed to modify the document, then we failed to update password.
            if result.modified_count == 0:
                return jsonify({
                    "status": "error",
                    "message": "Failed to update password."
                }), 501
            #Successfully changed password.
            response = make_response(jsonify({
                "status": "success",
                "message": "Successfully changed your password"
            }), 200)
            return response
            
        except Exception as e:
            #traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": f"Error connecting to database, check that out!"
            }), 500        
    else:
        return jsonify({"error": "Request must be JSON"}), 400

# Endpoint unsetting the JWT token as a cookie during logout.
@app.route('/logout', methods=['GET'])
def logout():
    response = make_response(jsonify({"message": "Logged out successfully"}), 200)
    unset_jwt_cookies(response)
    return response

#Endpoint that sends an email through the contact page to my email account.
@app.route('/send_email', methods=['POST'])
def send_email():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    print(data)
    # Retrieve necessary fields from payload.
    name = data.get("name")
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")

    try:
        #Retrieve the password used to authenticate into gmail's smtp server.
        secret = handling.get_email_secret(os.getenv("ACCESS_KEY_ID"), os.getenv("AWS_SECRET_ACCESS_KEY"))
        email_password = secret["PASSWORD"]
        if not email_password:
            raise ValueError("Email password not found in secrets")

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
    
@app.route('/get_password', methods=['POST'])
@jwt_required()
#Endpoint that fetches the password, JWT token required in order to retrieve it.
def get_password():
    user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": user_email})
    if user:
        decrypted_password = schema.User.from_mongo_document(schema.User, user).decrypt(user["original_password"])
        return jsonify({"password": decrypted_password}), 200
    return jsonify({"error": "User not found"}), 404
#Start the Flask app
if __name__ == '__main__':
    socketio.run(app, debug=True)