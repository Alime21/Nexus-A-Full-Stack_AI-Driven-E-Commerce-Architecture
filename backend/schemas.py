"""
NEXUS E-COMMERCE API - DATA VALIDATION & SCHEMA LAYER (PYDANTIC)
This module defines the strict data structures (schemas) for incoming requests
and outgoing responses. It enforces data integrity, validates formats (e.g., Email),
and ensures sensitive data (like passwords) is never leaked in responses.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# ==============================================================================
# DOMAIN: USER MANAGEMENT & AUTHENTICATION
# TARGET DATABASE: PostgreSQL (Relational)
# ==============================================================================

class UserCreate(BaseModel):
    """Schema for user registration payload. Enforces valid email format."""
    email: EmailStr  
    password: str

class UserResponse(BaseModel):
    """
    Schema for returning user data. 
    Notice that 'password' is intentionally omitted to prevent data leakage.
    """
    id: int
    email: str
    is_active: bool    

    class Config:
        # Allows Pydantic to read data directly from SQLAlchemy ORM models
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for the authentication (login) request payload."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for the JWT (JSON Web Token) returned upon successful authentication."""
    access_token: str
    token_type: str



# ==============================================================================
# DOMAIN: PRODUCT CATALOG
# TARGET DATABASE: MongoDB (NoSQL)
# ==============================================================================

class ProductBase(BaseModel):
    """
    Base schema for Products.
    Demonstrates the power of NoSQL with the 'attributes' field, 
    which accepts dynamic, flexible JSON data (e.g., RAM for laptops, size for clothing).
    """
    title: str = Field(..., example="MacBook Pro M3")
    description: str = Field(..., example="Apple 16GB RAM Laptop")
    price: float = Field(..., example=45999.99)
    stock: int = Field(default=0, example=50)
    category: str = Field(..., example="Electronic")
  
  # The flexible dictionary that makes MongoDB shine
    attributes: Optional[Dict[str, Any]] = Field(
        default={}, 
        example={"ram": "16GB", "cpu": "M3", "color": "Space Grey"}
    )

# when creating a product using productbase
class ProductCreate(ProductBase):
        """Schema for creating a new product. Inherits all fields from ProductBase."""
        pass

class ProductResponse(ProductBase):
        id: str = Field(..., alias="_id")

        class Config:
            # Allows the use of 'id' in Python while mapping it to '_id' in MongoDB
            populate_by_name = True