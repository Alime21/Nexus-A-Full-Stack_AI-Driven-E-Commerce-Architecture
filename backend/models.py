# --- USER DATA MODEL ---
# Purpose: To define the structure of the "users" table in the database using Python code. # Thanks to this class, instead of writing SQL directly to the database, we can perform user addition, deletion, and update operations with Python objects (ORM Logic).
# User addition, deletion, and update operations (ORM Logic).

from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"   # The actual table name in Postgres

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    is_admin = Column(Boolean, default=False)