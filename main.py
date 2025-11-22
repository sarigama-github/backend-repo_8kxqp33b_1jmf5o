import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Hotwheel

app = FastAPI(title="Hot Wheels Store API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility to convert Mongo docs
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


def serialize_doc(doc: dict):
    if not doc:
        return doc
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    return doc


class CreateHotwheel(BaseModel):
    name: str
    series: Optional[str] = None
    year: Optional[int] = None
    scale: Optional[str] = "1:64"
    condition: Optional[str] = "New"
    description: Optional[str] = None
    price: float
    stock: int = 1
    images: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    seller: Optional[str] = None


@app.get("/")
def root():
    return {"message": "Hot Wheels Store API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "❌ Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# Create a listing
@app.post("/api/hotwheels")
def create_hotwheel(item: CreateHotwheel):
    try:
        inserted_id = create_document("hotwheel", item.dict())
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List listings with optional search and filters
@app.get("/api/hotwheels")
def list_hotwheels(q: Optional[str] = None, series: Optional[str] = None, year: Optional[int] = None):
    try:
        filter_query = {}
        if q:
            # Basic text search across fields
            filter_query["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"series": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}},
            ]
        if series:
            filter_query["series"] = {"$regex": series, "$options": "i"}
        if year:
            filter_query["year"] = year

        docs = get_documents("hotwheel", filter_query)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get single listing
@app.get("/api/hotwheels/{item_id}")
def get_hotwheel(item_id: str):
    try:
        doc = db["hotwheel"].find_one({"_id": ObjectId(item_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Item not found")
        return serialize_doc(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
