"""
NEXUS E-COMMERCE API - MAIN GATEWAY
This file acts as the primary router for the FastAPI application.
It orchestrates incoming HTTP requests and routes them to the appropriate
services (Authentication, Product Catalog) across our Polyglot Persistence layer.
"""
# --- CORE IMPORTS ---
import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

# --- LOCAL MODULES & DATABASE CONNECTIONS ---
from database import engine, get_db, product_collection
import models, schemas, crud, utils

from bson.objectid import ObjectId

# --- DATABASE INITIALIZATION (POSTGRESQL) ---
# Automatically creates tables in PostgreSQL based on SQLAlchemy models (if they don't exist)
models.Base.metadata.create_all(bind=engine)

# --- FASTAPI APP INSTANCE ---
app = FastAPI(title="Nexus E-Commerce API", version="0.1.0")

# --- IMAGE STORAGE SETTINGS ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# We are making the "uploads" folder accessible to the internet with the name "/static".
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")    

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

# ---- Create Product (POST) -----
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

# ----- Get whole products (GET) -----
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

# ----- Get only one product (GET) -----
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

#  ----- Update product (PUT) -----
@app.put("/products/{product_id}", response_model=schemas.ProductResponse, tags=["Products"])
def update_product(product_id: str, product: schemas.ProductCreate):
    """
    Updates an existing product in MongoDB.
    First checks if the ID is valid, then performs the update.
    """
    # 1. ID Check
    try:
        obj_id = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Product ID format")

    # 2. find product and update
    # We are converting the incoming data (Pydantic) into a dictionary.
    update_data = product.model_dump()
    
    # We are telling MongoDB to "Find the document with this ID and replace its contents using the $set command"
    result = product_collection.update_one({"_id": obj_id}, {"$set": update_data})
    
    # 3. If nothing changes (or the product is not found), we might give an error.
    # However, here, we will consider it successful even if the product exists but the data is the same.

    # 4. We retrieve the updated product from the database again and show it to the user.
    updated_product = product_collection.find_one({"_id": obj_id})
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    updated_product["_id"] = str(updated_product["_id"])
    return updated_product

# ----- Delete product (DELETE) ------
@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(product_id: str):
    """
    Deletes a product from the database permanently.
    """
    # 1. ID Check
    try:
        obj_id = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Product ID format")

    # 2. Delete
    result = product_collection.delete_one({"_id": obj_id})
    
    # 3. If the number of deleted records is 0, it means the product does not exist.
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}

# ------ Product image Upload (IMAGE UPLOAD) -------
@app.post("/products/{product_id}/image", tags=["Products"])
async def upload_product_image(product_id: str, file: UploadFile = File(...)):
    """
    Uploads an image file for a specific product and updates the product's document in MongoDB.
    The image is stored locally in the 'uploads' directory.
    """

    # 1. ID CHECK
    try:
        obj_id = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Product ID format")
    
    # 2. VERIFY THE PRODUCT
    product = product_collection.find_one({"_id": obj_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 3. Create the File Name (We add the ID to the beginning to avoid conflicts)
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{product_id}_{file.filename}"
    file_location = f"{UPLOAD_DIR}/{unique_filename}"

    # 4. Save the file to disk.
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # 5. Add Image URL to Product in MongoDB    
    image_url = f"/static/{unique_filename}"
    
    product_collection.update_one(
        {"_id": obj_id},
        {"$set": {"image": image_url}}
    )
    
    return {"info": "Image uploaded successfully", "url": image_url}