"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Hot Wheels collection listings schema
class Hotwheel(BaseModel):
    """
    Hot Wheels die-cast car listing
    Collection name: "hotwheel"
    """
    name: str = Field(..., description="Car name or model")
    series: Optional[str] = Field(None, description="Series name, e.g., Mainline, Treasure Hunt")
    year: Optional[int] = Field(None, ge=1950, le=2100, description="Release year")
    scale: Optional[str] = Field("1:64", description="Scale, e.g., 1:64")
    condition: Optional[str] = Field("New", description="Condition, e.g., New, Loose, Carded")
    description: Optional[str] = Field(None, description="Description of the item")
    price: float = Field(..., ge=0, description="Price in USD")
    stock: int = Field(1, ge=0, description="Available quantity")
    images: Optional[List[HttpUrl]] = Field(default_factory=list, description="List of image URLs")
    tags: Optional[List[str]] = Field(default_factory=list, description="Keywords/tags for search")
    seller: Optional[str] = Field(None, description="Seller name or ID")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
