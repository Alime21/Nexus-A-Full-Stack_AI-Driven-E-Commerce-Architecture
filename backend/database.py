# --- DATABASE LAYER ---
# Purpose: To enable the application to communicate securely with the Postgres,MONGODB database,
# to manage database sessions, and
# to create the basic framework (Base) upon which our tables will be built.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient
import redis
import os

# ==============================================================================
# PostgreSQL CONNECTION SETTINGS (Users)
# ==============================================================================

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==============================================================================
# MONGODB CONNECTION SETTINGS (PRODUCT CATALOG)
# ==============================================================================

MONGO_URL = os.getenv("MONGO_URL")
mongo_client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
mongo_db = mongo_client["nexus_catalog"]
product_collection = mongo_db["products"]

# ==============================================================================
# REDIS CACHE CONNECTION (For Shopping Cart & Sessions)
# ==============================================================================

REDIS_URL = os.getenv("REDIS_URL", "redis://nexus_redis:6379/0")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_redis():
    """
    Dependency function to inject Redis client into FastAPI routes.
    """
    try:
        yield redis_client
    finally:
        # Redis connection pooling handles cleanup automatically
        pass