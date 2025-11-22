import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import User, Set as SetModel, CardMaster, UserCard, PricePoint, WishlistItem, TradeItem, Activity
from adapters import PokemonTCGAdapter, TCGPlayerAdapter, OCRAdapter, ImageMatchAdapter

app = FastAPI(title="Gotta Track 'Em API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment flags
USE_MOCKS = os.getenv("USE_MOCK_ADAPTERS", "true").lower() in ("1","true","yes")

# Instantiate adapters
pokemontcg = PokemonTCGAdapter()
tcgplayer = TCGPlayerAdapter()
ocr = OCRAdapter()
imgmatch = ImageMatchAdapter()

class SearchQuery(BaseModel):
    q: str

class AddUserCard(BaseModel):
    userId: str
    cardId: str
    finish: Optional[str] = "normal"
    language: Optional[str] = "en"
    condition: Optional[str] = "NM"
    quantity: int = 1

@app.get("/")
def read_root():
    return {"message": "Gotta Track 'Em backend ready"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["connection_status"] = "Connected"
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:100]}"
    return response

# Catalog endpoints (scaffold)
@app.get("/catalog/sets")
def list_sets():
    return pokemontcg.list_sets()

@app.get("/catalog/cards")
def search_cards(q: str):
    return pokemontcg.search_cards(q=q)

# Pricing endpoint (mocked or real depending on flag)
@app.post("/pricing")
def pricing(productIds: List[int]):
    return tcgplayer.get_prices_for_products(productIds)

# Scan to add pipeline (mock adapters)
@app.post("/scan/identify")
async def scan_identify(file: UploadFile = File(...)):
    img = await file.read()
    ocr_res = ocr.extract(img)
    sim_res = imgmatch.similar(img)
    return {"ocr": ocr_res, "candidates": sim_res}

# Collection endpoints
@app.get("/users/{user_id}/collection")
def get_collection(user_id: str):
    docs = get_documents("usercard", {"userId": user_id})
    return docs

@app.post("/users/{user_id}/collection")
def add_to_collection(user_id: str, item: AddUserCard):
    # Merge duplicate behavior: same userId+cardId+finish+language increments quantity
    existing = db["usercard"].find_one({
        "userId": user_id,
        "cardId": item.cardId,
        "finish": item.finish,
        "language": item.language,
    })
    if existing:
        new_qty = int(existing.get("quantity", 0)) + int(item.quantity)
        db["usercard"].update_one({"_id": existing["_id"]}, {"$set": {"quantity": new_qty, "updated_at": datetime.now(timezone.utc)}})
        created_id = str(existing["_id"])  # returning existing id
    else:
        created_id = create_document("usercard", {
            "userId": user_id,
            "cardId": item.cardId,
            "finish": item.finish,
            "language": item.language,
            "condition": item.condition,
            "quantity": item.quantity,
        })
    # Activity log
    create_document("activity", {
        "userId": user_id,
        "type": "collection.updated",
        "payload": {"cardId": item.cardId, "delta": item.quantity},
        "createdAt": datetime.utcnow(),
    })
    return {"ok": True, "id": created_id}

# Simple share token scaffold
@app.post("/share/create")
def create_share(userId: str, scope: Optional[Dict[str, Any]] = None, expiresAt: Optional[str] = None):
    import secrets
    token = secrets.token_urlsafe(24)
    create_document("share", {"userId": userId, "token": token, "scope": scope or {}, "expiresAt": expiresAt, "createdAt": datetime.utcnow()})
    return {"token": token}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
