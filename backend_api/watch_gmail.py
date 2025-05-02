from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os
import base64
import json
import subprocess
import time
import sys
import datetime
import requests
from pathlib import Path

try:
    from ML_Model import classify_email
    from ML_Model import classify_company_email
    print("✅ Successfully imported ML_Model.")
except Exception as e:
    print(f"❌ ERROR: Failed to import ML_Model. Details: {e}")
    exit(1)

# OAuth 2.0 Scopes for Gmail API
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify"
]

# Pub/Sub Topic Details
PROJECT_ID = "personified-449620"
TOPIC_NAME = f"projects/{PROJECT_ID}/topics/gmail-notifications"

# Store Seen Email IDs to Prevent Duplicates
seen_emails = set()

# OAuth Authentication
def get_credentials():
    creds = None
    # Get the directory containing the script
    script_dir = Path(__file__).parent
    token_path = script_dir / "token.pickle"
    secrets_path = script_dir / "client_secret.json"

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        print("🔑 No valid token found. Authenticating via OAuth...")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(secrets_path):
                raise FileNotFoundError(
                    "❌ client_secret.json not found. Please download OAuth credentials "
                    "from Google Cloud Console and save as 'client_secret.json' in the "
                    f"same directory as this script: {script_dir}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
        print("✅ New OAuth token saved.")

    return creds

# Start Gmail Watch Request
def watch_gmail():
    """Registers a Gmail watch request to receive email notifications via Pub/Sub."""
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    request_body = {
        "labelIds": ["INBOX"], 
        "topicName": TOPIC_NAME,
    }

    try:
        print("📡 Sending watch request to Gmail...")
        response = service.users().watch(userId="me", body=request_body).execute()
        print(f"✅ Gmail Watch Response: {response}")
    except Exception as e:
        print(f"❌ Error in watch request: {e}")

# Fetch Emails Using historyId
def get_new_emails(service, history_id):
    """Fetches all new emails received since the last historyId and avoids duplicates."""
    try:
        print(f"🔍 Checking Gmail API for historyId {history_id}...")
        history = service.users().history().list(userId="me", startHistoryId=history_id).execute()
        messages = history.get("history", [])

        if not messages:
            print("⚠️ No new emails found using historyId. Fetching the latest email manually...")
            fetch_latest_email(service)
            return

        for record in messages:
            if "messages" in record:
                for msg in record["messages"]:
                    msg_id = msg["id"]
                    if msg_id not in seen_emails:
                        seen_emails.add(msg_id)
                        print(f"📩 Fetching email with ID: {msg_id}")
                        fetch_email_by_id(service, msg_id)
                    else:
                        print(f"⚠️ Skipping duplicate email ID: {msg_id}")
    except Exception as e:
        print(f"❌ Error fetching emails with historyId {history_id}: {e}")
        print("⚠️ Falling back to manual fetch...")
        fetch_latest_email(service)

def fetch_email_by_id(service, msg_id):
    """Fetches and prints email details by message ID, including received date."""
    print(f"📨 Retrieving email content for message ID: {msg_id}...")
    message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    headers = message["payload"].get("headers", [])
    
    # Extract metadata
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
    date_received = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")

    # Convert the date to a standard format
    try:
        parsed_date = datetime.datetime.strptime(date_received, "%a, %d %b %Y %H:%M:%S %z")
        formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S %Z")  # Standard format
    except ValueError:
        formatted_date = date_received  # Fallback in case of parsing errors

    # Decode the email body
    body = "No Body Available"
    if "parts" in message["payload"]:
        for part in message["payload"]["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part["body"]:
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                break

    # 📌 Concatenating subject and body into "content"
    content = f"Subject: {subject}\nBody: {body}"

    company = classify_company_email(sender, content)

    print(f"\n📩 New Email Received!")
    print(f"📌 From: {sender}")
    print(f"📅 Received Date: {formatted_date}")
    print(f"📌 {content[:500]}") 

    # Classify the email content
    status = classify_email(content)

    email_data = {
        "user_email": "name@example.com",  #This should be the email of the logged in user.
        "date": formatted_date,
        "company": company,
        "company_email": sender,
        "role": role,
        "status": status
    }

    print("📌 Email Data:", email_data)

    if company != "not job related":
        print("Sending to process_application endpoint!")
        resp = requests.post('http://localhost:8000/process_application', json=email_data)
        if resp.ok:
            print(f"Application successfully processed: {resp.json()}")
        else:
            print(f'[Error] Received {resp.status_code} when sending to process_application')
    else:
        print("Email is not job related. Not sending to process application!")
     
    return email_data  

def fetch_latest_email(service):
    """Manually fetches the latest email from the inbox."""
    print("📬 Fetching latest email manually...")
    results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=1).execute()
    messages = results.get("messages", [])

    if messages:
        msg_id = messages[0]["id"]
        if msg_id not in seen_emails:
            seen_emails.add(msg_id)
            print(f"📨 Found latest email with ID: {msg_id}")
            fetch_email_by_id(service, msg_id)
        else:
            print(f"⚠️ Skipping duplicate latest email ID: {msg_id}")
    else:
        print("⚠️ No emails found in the inbox.")

# Listen for Emails via Pub/Sub
def listen_for_emails():
    """Continuously listens for new Gmail notifications via Pub/Sub and fetches emails."""
    service = build("gmail", "v1", credentials=get_credentials())

    while True:
        result = subprocess.run(
            ["gcloud", "pubsub", "subscriptions", "pull", "--auto-ack", "gmail-notifications-sub", "--format=json"],
            capture_output=True, text=True
        )

        if result.stdout.strip():
            try:
                messages = json.loads(result.stdout)
                data_found = False
                for msg in messages:
                    print("📡 Pub/Sub Notification Received.")
                    if "data" in msg:
                        print("🔍 Extracting email details from Pub/Sub...")
                        data = json.loads(msg["data"])
                        history_id = data.get("historyId")
                        if history_id:
                            print(f"🕵️ Processing historyId: {history_id}")
                            get_new_emails(service, history_id)
                            data_found = True
                if not data_found:
                    print("⚠️ No valid email data found in Pub/Sub. Checking manually...")
                    fetch_latest_email(service)
            except json.JSONDecodeError:
                print("⚠️ Error decoding Pub/Sub response. Skipping...")
        else:
            print("⚠️ No messages received from Pub/Sub. Checking manually...")
            fetch_latest_email(service)

        time.sleep(5)  # Wait 5 seconds before checking again

# Run the Script
if __name__ == "__main__":
    watch_gmail()  # Start watching Gmail for new messages
    listen_for_emails()  # Start listening for new emails