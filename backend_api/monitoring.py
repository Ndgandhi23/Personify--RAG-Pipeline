from pymongo import MongoClient
from bson.json_util import dumps
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
db = os.getenv("MONGO_DATABASE")
client = MongoClient(
    f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:"
    f"{os.getenv('MONGO_PASSWORD')}@"
    f"{os.getenv('MONGO_CLUSTER')}/"
    f"{db}"
    "?retryWrites=true&w=majority"
)
db = client[db]
questions_collection = db["questions"]

# Monitor the collection using Change Streams
def monitor_questions():
    with questions_collection.watch() as stream:
        for change in stream:
            # Extract the new question from the change document
            if change["operationType"] == "insert":
                new_question = change["fullDocument"]
                print("New question detected:", new_question)

                # Send a POST request to the API endpoint
                response = requests.post(
                    "http://127.0.0.1:5000/new_question",
                    json=new_question
                )
                if response.status_code == 200:
                    print("Question sent to API successfully.")
                else:
                    print("Failed to send question to API:", response.text)
            
if __name__ == "__main__":
    monitor_questions()