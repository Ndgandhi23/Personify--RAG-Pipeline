import boto3
from botocore.exceptions import BotoCoreError, ClientError
import json
# Function to retrieve the secrets from AWS Secrets Manager for securely contacting me.
def get_email_secret(access_key, secret_access_key):
    try:
        client = boto3.client(
            "secretsmanager",
            region_name="us-east-1",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
        )
        response = client.get_secret_value(
            SecretId="arn:aws:secretsmanager:us-east-1:412381777713:secret:Email_Password-uQRzUF",
            VersionStage="AWSCURRENT",
        )
        return json.loads(response["SecretString"])
    except (BotoCoreError, ClientError) as error:
        print(f"Error retrieving secret: {error}")
        raise error
    
# Method that calls the KMS client to decrypt the encryption key.
def decrypt_dek(encrypted_dek, access_key, secret_access_key):
    try:
        #Create a KMS client.
        client = boto3.client(
            "kms",
            region_name="us-east-1",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
        )
        #Send a request to decrypt user's encryption key for their password.
        response = client.decrypt(
            CiphertextBlob=encrypted_dek
        )
        return response["Plaintext"]
    except (BotoCoreError, ClientError) as error:
        print(f"Error decrypting DEK: {error}")
        raise error