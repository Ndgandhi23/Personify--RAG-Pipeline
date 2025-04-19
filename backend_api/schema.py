import base64
from cryptography.fernet import Fernet
import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

#Schemas for the user and application collections in the MongoDB database.
# schema.py
# schema.py
class User:
    # Generate a key for encryption/decryption (this should be securely stored and reused)
    def _initialize_encryption(self):
        """Initializes the encryption mechanism using AWS KMS."""
        # Initialize a session using Boto3
        access_key = os.getenv('ACCESS_KEY_ID')
        secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        session = boto3.session.Session(
            region_name="us-east-1",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key
        )

        # Create a KMS client
        kms_client = session.client('kms')

        # Specify the KMS key ID or ARN
        kms_key_id = os.getenv('KMS_ENCRYPTED_KEY_ID')
        try:
            # Generate a data encryption key using AWS KMS
            response = kms_client.generate_data_key(KeyId=kms_key_id, KeySpec='AES_256')
            # Use the plaintext data key for encryption, and store encrypted dek per user.
            self._encrypted_key = response['CiphertextBlob']
            # Use the plaintext DEK for encryption
            self._key = response['Plaintext']
        except NoCredentialsError:
            print("AWS credentials not found. Please configure them.")
            raise
        except Exception as e:
            print(f"Error generating data key: {str(e)}")
            raise

    def __init__(self, email, password, original_password, encrypted, searches=None, encrypted_dek=None):
        self.email = email
        self.password = password
        self.encrypted = encrypted
        #For new documents
        if not encrypted:
            load_dotenv()
            self._initialize_encryption() #Setting up encryption mechanisms.
        self.original_password = self._encrypt(original_password) if not encrypted else original_password  # Encrypt the original password
        self.key = '' #Discard the plaintext key.
        if encrypted_dek:
            self._encrypted_key = encrypted_dek
        self.searches = []
        
    #Creating a user object from an existing Personify user profile as a mongodb document.
    @classmethod
    def from_mongo_document(cls, document):
        """Creates a User instance from a MongoDB document."""
        email = document.get("email")
        password = document.get("password")
        original_password = document.get("original_password")
        searches = document.get("searches", [])
        encrypted_dek = document.get("encrypted_dek")

        instance = cls(email, password, original_password, True, searches, encrypted_dek)
        return instance

    def _encrypt(self, data):
        """Encrypts the given data using AES-256."""
        cipher = Cipher(algorithms.AES(self._key), modes.GCM(b'16_byte_nonce'))
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data.encode()) + encryptor.finalize()
        return base64.b64encode(encrypted_data).decode()

    def _decrypt(self, encrypted_data):
        """Decrypts the given encrypted data using AES-256."""
        cipher = Cipher(algorithms.AES(self._key), modes.GCM(b'16_byte_nonce'))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(base64.b64decode(encrypted_data)) + decryptor.finalize()
        return decrypted_data.decode()

    def get_original_password(self):
        """Returns the decrypted original password."""
        return self._decrypt(self.original_password)

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password,
            "original_password": self.original_password,  # Store encrypted original password
            "searches": self.searches,
            "encrypted_dek": self._encrypted_key #Encrypted for secure purposes.
        }

#Class Schema for our applications on MongoDB.
class Application:
    def __init__(self, user_email, date, company, company_email, role, status):
        self.user_email = user_email  # Linked to the email of the logged-in user
        self.date = date              # Date the application was created or updated
        self.company = company        # Company the application is being submitted to
        self.company_email = company_email  # The email of the company sending the notification
        self.role = role              # The role for which the application is being submitted
        self.status = status          # The current status of the application (e.g., Pending, Accepted)

    def to_dict(self):
        return {
            "user_email": self.user_email,
            "date": self.date,
            "company": self.company,
            "company_email": self.company_email,
            "role": self.role,
            "status": self.status
        }