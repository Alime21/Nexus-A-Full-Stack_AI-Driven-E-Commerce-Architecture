# ---------- Security room ----------------------------
# Password Security: Hashes passwords with 'bcrypt' (get_password_hash)
# and checks its validity upon login (verify_password).
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)