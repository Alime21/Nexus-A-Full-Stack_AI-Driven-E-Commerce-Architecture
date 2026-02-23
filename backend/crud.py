# --------------- Database Workers ------------------------
# Database Operations: Queries user by email (get_user_by_email)
# and hashes the password to save the new user to the DB (create_user).
from sqlalchemy.orm import Session
import models, schemas, utils

def get_user_by_email(db: Session, email: str):
    """This email checks the database to see if someone has registered before using this email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    # 1. Encrypt (Hash) the password
    hashed_password = utils.get_password_hash(user.password)
    
    # 2. Create the ORM Model (Python Class)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    
    # 3. Add to and save the database.
    db.add(db_user)
    db.commit()
    db.refresh(db_user) 
    
    return db_user