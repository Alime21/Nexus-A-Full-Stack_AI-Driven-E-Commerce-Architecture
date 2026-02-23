# This file is the gateway to our Nexus E-Commerce API. 
# Its main purpose is to verify that the server is active (Health Check) and
# to establish the main structure that will start the FastAPI engine and direct all incoming HTTP requests to the correct functions.
from fastapi import FastAPI
from database import engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus E-Commerce API")

@app.get("/")
def health_check():
    return {"status": "Sistem Up and Running!", "message": "Nexus API is running successfully"}