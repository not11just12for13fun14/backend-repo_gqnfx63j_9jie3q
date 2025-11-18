import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import create_document, get_documents, db
from schemas import QuoteRequest, Shipment

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ---------------- Transport API ----------------

@app.post("/api/quote")
def create_quote(quote: QuoteRequest):
    """Create a quote request. Persists to the database."""
    try:
        inserted_id = create_document("quoterequest", quote)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/track/{tracking_number}")
def track_shipment(tracking_number: str):
    """Return shipment details for a tracking number."""
    try:
        docs = get_documents("shipment", {"tracking_number": tracking_number}, limit=1)
        if not docs:
            raise HTTPException(status_code=404, detail="Tracking number not found")
        doc = docs[0]
        # Convert ObjectId and datetimes to strings for JSON safety
        doc["_id"] = str(doc.get("_id"))
        for key in ["eta", "last_update"]:
            if isinstance(doc.get(key), datetime):
                doc[key] = doc[key].isoformat()
        # events may include datetimes
        events = doc.get("events") or []
        for e in events:
            ts = e.get("timestamp")
            if isinstance(ts, datetime):
                e["timestamp"] = ts.isoformat()
        return {"ok": True, "shipment": doc}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NewShipment(BaseModel):
    tracking_number: str
    origin: str
    destination: str
    status: str = "In Transit"
    eta: Optional[datetime] = None


@app.post("/api/shipments")
def create_shipment(payload: NewShipment):
    """Helper endpoint to create a shipment for testing/tracking demos."""
    try:
        # Build shipment document
        shipment = {
            "tracking_number": payload.tracking_number,
            "origin": payload.origin,
            "destination": payload.destination,
            "status": payload.status,
            "eta": payload.eta or datetime.utcnow(),
            "last_update": datetime.utcnow(),
            "events": [
                {
                    "timestamp": datetime.utcnow(),
                    "location": payload.origin,
                    "description": "Shipment created",
                }
            ],
        }
        inserted_id = create_document("shipment", shipment)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
