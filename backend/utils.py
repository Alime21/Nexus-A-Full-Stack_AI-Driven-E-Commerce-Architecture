# ---------- Security room ----------------------------
# Password Security: Hashes passwords with 'bcrypt' (get_password_hash)
# and checks its validity upon login (verify_password).
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

# our Bcrypt encryption machine
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --------- JWT ------------------
SECRET_KEY = "nexus_secret_key_word" # Our signature to prevent the cards from being counterfeited.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # VIP card validity period (60 minutes)

def create_access_token(data: dict):
    """It prints the VIP card (JWT) to be given to the customer."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Create the card and sign it with our private key.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt