"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# -------------------- Example schemas (kept for reference) --------------------
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# -------------------- Transport app schemas --------------------
class QuoteRequest(BaseModel):
    """
    Quote requests collection
    Collection name: "quoterequest"
    """
    name: str = Field(..., description="Contact name")
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    company: Optional[str] = Field(None, description="Company name")

    cargo_type: str = Field(..., description="Type of cargo (e.g., pallets, reefer, flatbed)")
    weight_kg: Optional[float] = Field(None, ge=0, description="Approximate total weight in kg")
    dimensions_cm: Optional[str] = Field(None, description="Dimensions or LxWxH per unit in cm")

    pickup_location: str = Field(..., description="Pickup city/state or address")
    delivery_location: str = Field(..., description="Delivery city/state or address")
    preferred_pickup_date: Optional[str] = Field(None, description="Preferred pickup date (YYYY-MM-DD)")
    preferred_delivery_date: Optional[str] = Field(None, description="Preferred delivery date (YYYY-MM-DD)")

    notes: Optional[str] = Field(None, description="Additional details or special handling")

class ShipmentEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[str] = None
    description: str

class Shipment(BaseModel):
    """
    Shipments collection
    Collection name: "shipment"
    """
    tracking_number: str = Field(..., description="Unique tracking number")
    status: str = Field(..., description="Current status (In Transit, Delivered, etc.)")
    origin: str = Field(..., description="Origin city/state")
    destination: str = Field(..., description="Destination city/state")
    eta: Optional[datetime] = Field(None, description="Estimated delivery time")
    last_update: Optional[datetime] = Field(default_factory=datetime.utcnow)
    events: List[ShipmentEvent] = Field(default_factory=list, description="Tracking history events")
