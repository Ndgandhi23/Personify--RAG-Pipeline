#Useful for secure password validation.
import warnings
from cryptography.utils import CryptographyDeprecationWarning
from werkzeug.security import generate_password_hash, check_password_hash

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

def hash_password(password: str) -> str:
    return generate_password_hash(password, method='pbkdf2:sha256:260000')

def verify_password(password: str, hash: str) -> bool:
    return check_password_hash(hash, password)