# This file is the gateway to our Nexus E-Commerce API. 
# Its main purpose is to verify that the server is active (Health Check) and
# to establish the main structure that will start the FastAPI engine and direct all incoming HTTP requests to the correct functions.
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud

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