"""
NEXUS E-COMMERCE API - MAIN GATEWAY
===================================
This file acts as the primary router for the FastAPI application.
It orchestrates incoming HTTP requests and routes them to the appropriate
services (Authentication, Product Catalog) across our Polyglot Persistence layer.
"""

# --- 1. STANDARD LIBRARY IMPORTS ---
import os
import shutil
from typing import List, Optional

# --- 2. THIRD PARTY IMPORTS ---
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from bson.objectid import ObjectId

# --- 3. LOCAL APPLICATION IMPORTS ---
import models
import schemas
import crud
import utils
from database import engine, get_db, product_collection


# --- 4. DATABASE INITIALIZATION (Relational) ---
# Automatically creates tables in PostgreSQL if they don't exist
models.Base.metadata.create_all(bind=engine)

# --- 5. APP CONFIGURATION -------
app = FastAPI(title="Nexus E-Commerce API", version="0.1.0")

# --- 6. STATIC FILE CONFIGURATION (Local Storage) ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# We are making the "uploads" folder accessible to the internet with the name "/static".
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")    



# ==============================================================================
# MODULE 1: AUTHENTICATION SERVICE
# DATABASE: PostgreSQL (Relational)
# ==============================================================================

@app.post("/register", response_model=schemas.UserResponse, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user. Checks for existing email and hashes password.
    """
    # 1. Check if the user already exists in the relational database
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="This email address is already registered!")
    return crud.create_user(db=db, user=user)


@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates user and returns a JWT access token.
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
# MODULE 2: PRODUCT CATALOG SERVICE
# DATABASE: MongoDB (NoSQL)
# ==============================================================================

@app.post("/products", response_model=schemas.ProductResponse, tags=["Products"])
def create_product(product: schemas.ProductCreate):
    """
    Creates a new product document in MongoDB.
    """
    product_dict = product.model_dump()
    result = product_collection.insert_one(product_dict)
    
    # Convert ObjectId to string for response
    product_dict["_id"] = str(result.inserted_id)
    return product_dict


@app.get("/products", response_model=list[schemas.ProductResponse], tags=["Products"])
def get_products():
    """
    Retrieves all products from the MongoDB catalog.
    """
    products = list(product_collection.find())
    
    # Serialize ObjectId for all items
    for prod in products:
        prod["_id"] = str(prod["_id"]) 
    return products


@app.get("/products/{product_id}", response_model=schemas.ProductResponse, tags=["Products"])
def get_product(product_id: str):
    """
    Retrieves a single product by ID.
    """
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid Product ID format")
    
    obj_id = ObjectId(product_id)
    product = product_collection.find_one({"_id": obj_id})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product["_id"] = str(product["_id"])
    return product


@app.put("/products/{product_id}", response_model=schemas.ProductResponse, tags=["Products"])
def update_product(product_id: str, product: schemas.ProductCreate):
    """
    Updates product attributes.
    """
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid Product ID format")

    obj_id = ObjectId(product_id)
    update_data = product.model_dump()
    
    result = product_collection.update_one(
        {"_id": obj_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    updated_product = product_collection.find_one({"_id": obj_id})
    updated_product["_id"] = str(updated_product["_id"])
    return updated_product
    

@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(product_id: str):
    """
    Deletes a product from the database permanently.
    """
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid Product ID format")

    obj_id = ObjectId(product_id)
    result = product_collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}



# ==============================================================================
# MODULE 3: MEDIA SERVICE (CURRENT: LOCAL STORAGE)
# ==============================================================================

@app.post("/products/{product_id}/image", tags=["Products"])
async def upload_product_image(product_id: str, file: UploadFile = File(...)):
    """
    Uploads a product image to local storage.
    Note: This endpoint will be refactored for AWS S3.
    """
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid Product ID format")
    
    obj_id = ObjectId(product_id)
    product = product_collection.find_one({"_id": obj_id})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Generate unique filename
    # unique_filename = f"{product_id}_{file.filename}"
    # Sanitizing filename is a good practice, but keeping simple for now
    unique_filename = f"{product_id}_{file.filename.replace(' ', '_')}"
    file_location = f"{UPLOAD_DIR}/{unique_filename}"

    try:
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    # Update Database
    image_url = f"/static/{unique_filename}"
    
    product_collection.update_one(
        {"_id": obj_id},
        {"$set": {"image": image_url}}
    )
    
    return {"info": "Image uploaded successfully", "url": image_url}