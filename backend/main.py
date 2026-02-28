"""
NEXUS E-COMMERCE API - MAIN GATEWAY
This file acts as the primary router for the FastAPI application.
It orchestrates incoming HTTP requests and routes them to the appropriate
services (Authentication, Product Catalog) across our Polyglot Persistence layer.
"""
# --- CORE IMPORTS ---
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# --- LOCAL MODULES & DATABASE CONNECTIONS ---
from database import engine, get_db, product_collection
import models, schemas, crud, utils

from bson.objectid import ObjectId

# --- DATABASE INITIALIZATION (POSTGRESQL) ---
# Automatically creates tables in PostgreSQL based on SQLAlchemy models (if they don't exist)
models.Base.metadata.create_all(bind=engine)

# --- FASTAPI APP INSTANCE ---
app = FastAPI(title="Nexus E-Commerce API", version="0.1.0")



# ==============================================================================
# DOMAIN: USER MANAGEMENT & AUTHENTICATION
# DATABASE: PostgreSQL (Relational, ACID Compliant)
# ==============================================================================

@app.post("/register", response_model=schemas.UserResponse, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the PostgreSQL database.
    Includes email duplication check and secure password hashing.
    """
    # 1. Check if the user already exists in the relational database
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="This email address is already registered!")
    return crud.create_user(db=db, user=user)


@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user and issues a stateless JWT (JSON Web Token) for session management.
    """
    # 1. Verify credentials against the PostgreSQL database
    user = crud.authenticate_user(db, email=user_credentials.email, password=user_credentials.password)
    
    if not user:
        raise HTTPException(status_code=400, detail="E-posta veya şifre hatalı!")
    
   # 2. Generate the JWT (Access Token) for the authenticated user
    access_token = utils.create_access_token(data={"sub": user.email})
    # 3. Return the token to the client
    return {"access_token": access_token, "token_type": "bearer"}



# ==============================================================================
# DOMAIN: PRODUCT CATALOG
# DATABASE: MongoDB (NoSQL, Document-Based, Flexible Schema)
# ==============================================================================

@app.post("/products", response_model=schemas.ProductResponse, tags=["Products"])
def create_product(product: schemas.ProductCreate):
    """
    Adds a new product to the MongoDB catalog. 
    Utilizes a flexible schema allowing dynamic attributes (e.g., RAM, color, size).
    """
    # 1. Convert the Pydantic model into a Python dictionary (JSON-like structure)
    product_dict = product.model_dump()
    # 2. Insert the document directly into the MongoDB collection
    result = product_collection.insert_one(product_dict)
    # 3. Extract the auto-generated MongoDB ObjectId and convert it to a string for the frontend
    product_dict["_id"] = str(result.inserted_id)
    # 4. Return the newly created product document
    return product_dict

@app.get("/products", response_model=list[schemas.ProductResponse], tags=["Products"])
def get_products():
    """
    Retrieves all products from the MongoDB catalog.
    Converts MongoDB ObjectIds to strings for frontend compatibility.
    """
    # 1. Fetch all documents from the 'products' collection and cast the cursor to a Python list
    products = list(product_collection.find())
    
    # 2. Iterate through the products to convert the non-serializable BSON ObjectId to a standard string
    for prod in products:
        prod["_id"] = str(prod["_id"])
        
    # 3. Return the sanitized list to the client    
    return products


@app.get("/products/{product_id}", response_model=schemas.ProductResponse, tags=["Products"])
def get_product(product_id: str):
    """
    Retrieves a specific product by its unique MongoDB identifier.
    Includes validation to ensure the provided ID matches the valid BSON ObjectId format.
    """
    # 1. Attempt to cast the incoming string ID to a MongoDB ObjectId
    try:
        obj_id = ObjectId(product_id)
    except Exception:
        # If the format is strictly invalid (e.g., non-hexadecimal), throw a 400 error immediately
        raise HTTPException(status_code=400, detail="Invalid Product ID format")
    
    # 2. Query the MongoDB database for a document matching this exact ObjectId
    product = product_collection.find_one({"_id": obj_id})
    
    # 3. If no document matches the query, gracefully return a 404 Not Found error
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 4. Convert the BSON ObjectId to a string before returning the JSON payload
    product["_id"] = str(product["_id"])
    return product