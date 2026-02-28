# --- DATA VALIDATION AND SCHEMA LAYER ---
# Purpose: To define the structure of data coming to (Request) and going from (Response) the API,
# to check the accuracy of the data (email format, etc.) and to filter sensitive data (such as passwords) to prevent leakage.

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr  
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool    

    class Config:
        from_attributes = True

# The form the customer will fill out when logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# The format of the VIP Card we will give to our customer
class Token(BaseModel):
    access_token: str
    token_type: str