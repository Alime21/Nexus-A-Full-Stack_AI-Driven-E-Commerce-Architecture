from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy import Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# ==============================================================================
# USER MODELS (ORM Logic)
# ==============================================================================

class User(Base):
    __tablename__ = "users"   # The actual table name in Postgres

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    is_admin = Column(Boolean, default=False)

# ==============================================================================
# ORDER MODELS (POSTGRESQL)
# ==============================================================================    
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)  
    total_amount = Column(Float, default=0.0) 
    status = Column(String, default="pending") 
    created_at = Column(DateTime, default=datetime.utcnow) 

    # An order can have more than one item (OrderItem).
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id")) # Which order does this belong to?
    product_id = Column(String) # Product ID in MongoDB
    quantity = Column(Integer)
    price_at_purchase = Column(Float) # Current purchase price of the product (to avoid future price increases and ensure the invoice remains valid)

    order = relationship("Order", back_populates="items")