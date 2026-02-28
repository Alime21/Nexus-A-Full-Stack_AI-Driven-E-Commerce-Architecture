# This file is the gateway to our Nexus E-Commerce API. 
# Its main purpose is to verify that the server is active (Health Check) and
# to establish the main structure that will start the FastAPI engine and direct all incoming HTTP requests to the correct functions.
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud, utils

# create tables (migration)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus E-Commerce API")

# -------- Newly added registration route --------------
@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="This email address is already registered!")
    return crud.create_user(db=db, user=user)

# ---- health check --------
@app.get("/")
def health_check():
    return {"status": "Sistem Up and Running!", "message": "Nexus API is running successfully"}


# --------- LOGIN Roadmap ----------------------
@app.post("/login", response_model=schemas.Token)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. Verify the customer's identity (send it to the function in crud.py)
    user = crud.authenticate_user(db, email=user_credentials.email, password=user_credentials.password)
    
    if not user:
        # 2. If the ID is incorrect, call security (Throw a bug report).
        raise HTTPException(status_code=400, detail="E-posta veya şifre hatalı!")
    
    # 3. If the identification is correct, print the VIP card from the printing press and give it to the customer.
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}