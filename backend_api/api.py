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
import requests
import logging
from datetime import datetime




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
    
# Set up logging mechanisms for this application.
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

# Create a formatter with timestamps
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File handler - logs to a file with date in the filename
log_file = os.path.join(log_directory, f"app_{datetime.now().strftime('%Y%m%d')}.log")
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)

# Console handler - logs to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Create logger
logger = logging.getLogger('personify-api')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

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
    print(query)
    
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
        results = list(applications_collection.find(query))
        #Convert each application's object id into a string.
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

        # For the future -> Create a vector based on user email, company, and role to identify application.
        # Put automation/vectorization code here!
        
        # Put automation/vectorization code here!
        # Insert/Update the application into MongoDB
        try:
            applications_collection = mongo.db.applications
            
            #updates application status
            applications_collection.update_one(
                {"user_email": user_email, "company": company, "role": role},
                {"$set": {"date": date, "company_email": company_email, "status": status}},
                upsert=True  # Create a new document if no document matches the query
            )
            # Emit a dictionary of field names mapped to their values to the frontend
            field_values = {
                "company": company,
                "date": date,
                "role": role,
                "user_email": user_email,
                "company_email": company_email,
                "status": status
            }
            socketio.emit('application_processed', field_values, room=request.sid)
            #Success message back to the monitoring script.
            return jsonify({"message": "Application processed successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/last-search', methods=['POST'])
#Put JWT required
def get_last_search():
    try:
        # Get the email from the request payload
        data = request.get_json()
        user_email = data.get("email")
        
        if not user_email:
            return jsonify({"error": "Email is required"}), 400
        
        # Fetch the user's document from the database
        user = mongo.db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Retrieve the most recent search from the user's searches
        searches = user.get("searches", [])
        last_search = searches[0] if searches else {}
        last_search["user_email"] = user_email
        print(last_search)
        return jsonify(last_search), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

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

#Endpoint that handles automatic key rotation every 90 days
#running in the background.
@app.route('/rotate-keys', methods=['POST'])
def rotate_keys():
    data = request.get_json()
    print(f"Received data: {data}")  # Log the full payload

    if 'SubscribeURL' in data:
        logger.info(f"Processing subscription confirmation: {data['SubscribeURL']}")
        # Confirm the subscription
        requests.get(data['SubscribeURL'])
        return jsonify({"message": "Subscription confirmed"}), 200

    # Handle SNS notification structure
    if data and 'Type' in data and data['Type'] == 'Notification':
        try:
            # Extract the message content
            message = json.loads(data.get('Message', '{}'))
            event_name = message.get('eventName')

            # Log the rotation event details
            logger.info(f"Received KMS event: {event_name}")
            # More detailed logging for the rotation event.
            rotated_key_id = message.get('requestParameters', {}).get('keyId')
            logger.info(f"Key affected: {rotated_key_id}")
            # Check if this is a KMS key rotation event
            if event_name and 'Rotate' in event_name:
                # Implement your key rotation logic here
                # This should handle re-encrypting user data with the new key
                logger.info("Key rotation detected, processing...")

                users_collection = mongo.db.users
                users = users_collection.find()
                user_count = users_collection.count_documents({})
                logger.info(f"Processing {user_count} users for key rotation")
                
                updated_count = 0

                # For each user document
                for user in users:
                    logger.debug(f"Processing user: {user['email']}")
                    # Creating a new user object from that document
                    user_obj = schema.User.from_mongo_document(user)
                    try:
                        access_key = os.getenv("ACCESS_KEY_ID")
                        secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
                    except ValueError as e:
                        return jsonify({
                            "status": "error",
                            "message": "AWS credentials are missing in the environment variables."
                        }), 500

                    # Decrypt the encrypted key from the user object
                    decrypted_dek = handling.decrypt_dek(user_obj._encrypted_key, access_key, secret_access_key)

                    # Use that to decrypt the user obj's password
                    user_obj._key = decrypted_dek
                    decrypted_password = user_obj._decrypt(user_obj.original_password)
                    user_obj._key = ''

                    # Initialize encryption process again
                    decrypted_dek = user_obj._initialize_encryption()

                    # Encrypt the obj.password through the obj.key
                    encrypted_password = user_obj._encrypt(user_obj.original_password)

                    # Discard the key once encrypted (Set to empty)
                    user_obj._key = ''

                    # Now update the document classified by id
                    users_collection.update_one(
                        {"_id": user["_id"]},
                        {"$set": {
                            "original_password": encrypted_password,
                            "_encrypted_key": user_obj._encrypted_key
                        }}
                    )
                    
                    updated_count += 1
                    logger.info(f"Successfully re-encrypted data for {updated_count} users")
                return jsonify({"message": f"Data encrypted successfully after key rotation event: {event_name}"}), 200

        except Exception as e:
            logger.error(f"Error processing key rotation: {str(e)}", exc_info=True)
            return jsonify({"error": f"Failed to process notification: {str(e)}"}), 500

    # Unknown format
    logger.warning(f"Received unknown request format: {data}")
    return jsonify({"message": "Unknown request format"}), 400

#Start the Flask app
if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000)