# --- DATABASE LAYER ---
# Purpose: To enable the application to communicate securely with the Postgres database,
# to manage database sessions, and
# to create the basic framework (Base) upon which our tables will be built.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://nexus_user:nexus_password@postgres_db:5432/nexus_core_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()