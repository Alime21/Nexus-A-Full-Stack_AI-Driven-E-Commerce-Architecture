"""
NEXUS E-COMMERCE API - MAIN GATEWAY
===================================
This file acts as the primary router for the FastAPI application.
It orchestrates incoming HTTP requests and routes them to the appropriate
services (Authentication, Product Catalog) across our Polyglot Persistence layer.
"""

# --- 1. STANDARD LIBRARY IMPORTS ---
import stripe
import os
import shutil
from typing import List, Optional
from database import engine, get_db, product_collection, get_redis

# --- 2. THIRD PARTY IMPORTS ---
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from bson.objectid import ObjectId
import redis

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

# Stripe Setting
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_dummy_key")



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

# ==============================================================================
# MODULE 4: SHOPPING CART SERVICE (REDIS - IN MEMORY CACHE)
# ==============================================================================
@app.post("/cart/{user_email}/add", tags=["Shopping Cart"])
def add_to_cart(user_email: str, item: schemas.CartItemAdd, redis_client: redis.Redis = Depends(get_redis)):
    """
    Adds a product to the user's shopping cart in Redis.
    Uses Redis Hash (HINCRBY) to store user carts efficiently.
    """
    # 1. We can check if this product actually exists on MongoDB (Optional but safe)
    if not ObjectId.is_valid(item.product_id):
        raise HTTPException(status_code=400, detail="Invalid Product ID")
    
    product = product_collection.find_one({"_id": ObjectId(item.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in catalog")
    # 2. Create the shopping cart key in Redis 
    cart_key = f"cart:{user_email}"
    
    # 3. Add the product and its quantity to the Redis Hash (HINCRBY: Increments the quantity if it exists, otherwise creates it)
    redis_client.hincrby(cart_key, item.product_id, item.quantity)
    
    return {"message": f"Added {item.quantity} units of product to {user_email}'s cart"}


@app.get("/cart/{user_email}", tags=["Shopping Cart"])
def get_cart(user_email: str, redis_client: redis.Redis = Depends(get_redis)):
    """
    Retrieves the entire shopping cart for a user from Redis.
    """
    cart_key = f"cart:{user_email}"
    
    # Retrieve all data from that user's shopping cart from Redis (HGETALL)
    cart_data = redis_client.hgetall(cart_key)
    
    if not cart_data:
        return {"user": user_email, "cart": {}, "message": "Cart is empty"}
        
    return {"user": user_email, "cart": cart_data}


@app.delete("/cart/{user_email}/remove/{product_id}", tags=["Shopping Cart"])
def remove_from_cart(user_email: str, product_id: str, redis_client: redis.Redis = Depends(get_redis)):
    """
    Removes a specific product from the user's cart.
    """
    cart_key = f"cart:{user_email}"
    
    # Remove that product from Redis Hash (HDEL)
    result = redis_client.hdel(cart_key, product_id)
    
    if result == 0:
         raise HTTPException(status_code=404, detail="Product not found in cart")
         
    return {"message": "Product removed from cart"}


# ==============================================================================
# CHECKOUT & ORDER PROCESSING (THE POLYGLOT MAGIC)
# ==============================================================================

@app.post("/checkout/{user_email}", response_model=schemas.OrderResponse, tags=["Shopping Cart"])
def checkout(user_email: str, request: schemas.CheckoutRequest, db: Session = Depends(get_db), redis_client: redis.Redis = Depends(get_redis)):
    """
    1. Reads the cart from Redis.
    2. Verifies prices and product existence from MongoDB.
    3. Creates a permanent Order and OrderItems in PostgreSQL.
    4. Clears the Redis cart upon success.
    """
    cart_key = f"cart:{user_email}"
    cart_data = redis_client.hgetall(cart_key)
    
    # Shopping Basket/Cart empty check (Redis)
    if not cart_data:
        raise HTTPException(status_code=400, detail="Checkout failed: Cart is empty")
    
    total_amount = 0.0
    order_items_ready = []
    
# ------ 1. MONGODB: Verify Products and Prices ------------
    for product_id_str, quantity_str in cart_data.items():
        quantity = int(quantity_str)
        product = product_collection.find_one({"_id": ObjectId(product_id_str)})
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id_str} no longer exists")
        
        # We retrieve the current price from MongoDB.
        current_price = float(product.get("price", 0.0))
        total_amount += current_price * quantity
        
        order_items_ready.append(
            models.OrderItem(product_id=product_id_str, quantity=quantity, price_at_purchase=current_price)
        )

# --------- 2. STRIPE: RECEIVING PAYMENT -----------
    try:
        charge = stripe.Charge.create(
            amount=int(total_amount * 100),
            currency="try", 
            source=request.payment_token, 
            description=f"Nexus Order for {user_email}"
        )
        order_status = "paid"
        
    except stripe.error.StripeError as e:
        print(f"Stripe Test Hatası (Beklenen bir durum): {e}")
        order_status = "payment_failed"  


#---------- 3. POSTGRESQL: SAVE ORDERS  ---------
    new_order = models.Order(
        user_email=user_email,
        total_amount=total_amount,
        status=order_status
    )
    
    db.add(new_order)
    db.commit()      # To assign an ID to the order, we first need to record this.
    db.refresh(new_order)
    
   
    # We are linking the sub-items we have prepared to this order (order_id).
    for item in order_items_ready:
        item.order_id = new_order.id
        db.add(item)
        
    db.commit()      # We also permanently record the pens.
    db.refresh(new_order)
    
# ------- 4. REDIS: CLEAN SHOPPING CART  ---------
    if order_status == "paid":
        redis_client.delete(cart_key)
    
    return new_order