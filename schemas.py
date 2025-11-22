"""
Database Schemas for Gotta Track 'Em

Each Pydantic model represents a collection in MongoDB. The collection name is the lowercase
of the class name (e.g., User -> "user").
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Core entities from spec

class User(BaseModel):
    id: Optional[str] = Field(default=None, description="User id (ObjectId as str)")
    email: str
    displayName: Optional[str] = None
    avatarUrl: Optional[str] = None
    authProvider: Optional[str] = Field(default="password", description="password|google|apple|magic")
    currency: Optional[str] = Field(default="USD")
    region: Optional[str] = Field(default="US")
    createdAt: Optional[datetime] = None

class Set(BaseModel):
    id: str
    name: str
    series: Optional[str] = None
    total: Optional[int] = None
    printedTotal: Optional[int] = None
    logo: Optional[str] = None
    symbol: Optional[str] = None
    releaseDate: Optional[str] = None
    legalities: Optional[Dict[str, Any]] = None
    tcgplayerSetId: Optional[str] = None

class CardImages(BaseModel):
    small: Optional[str] = None
    large: Optional[str] = None

class CardVariants(BaseModel):
    normal: Optional[bool] = None
    reverse: Optional[bool] = None
    holo: Optional[bool] = None
    foil: Optional[bool] = None
    rainbow: Optional[bool] = None
    gold: Optional[bool] = None

class Legalities(BaseModel):
    standard: Optional[str] = None
    expanded: Optional[str] = None

class CardMaster(BaseModel):
    id: str
    name: str
    setId: str
    setName: Optional[str] = None
    number: str
    rarity: Optional[str] = None
    types: Optional[List[str]] = None
    subtypes: Optional[List[str]] = None
    supertype: Optional[str] = None
    illustrator: Optional[str] = None
    regulationMark: Optional[str] = None
    legalities: Optional[Legalities] = None
    images: Optional[CardImages] = None
    variants: Optional[CardVariants] = None
    releaseDate: Optional[str] = None
    languageCodes: Optional[List[str]] = None

class UserCard(BaseModel):
    id: Optional[str] = None
    userId: str
    cardId: str
    finish: Optional[str] = Field(default="normal")
    language: Optional[str] = Field(default="en")
    condition: Optional[str] = Field(default="NM")
    quantity: int = Field(default=1, ge=0)
    purchasePrice: Optional[float] = None
    purchaseCurrency: Optional[str] = Field(default="USD")
    acquiredAt: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    sleeve: Optional[bool] = None
    graded: Optional[bool] = None
    gradeVendor: Optional[str] = None
    gradeScore: Optional[str] = None
    acquisitionSource: Optional[str] = None
    lastValuation: Optional[float] = None
    lastValuationAt: Optional[datetime] = None

class PricePoint(BaseModel):
    id: Optional[str] = None
    cardId: str
    finish: Optional[str] = None
    market: Optional[float] = None
    low: Optional[float] = None
    mid: Optional[float] = None
    high: Optional[float] = None
    timestamp: datetime
    source: str

class WishlistItem(BaseModel):
    id: Optional[str] = None
    userId: str
    cardId: str
    targetPrice: Optional[float] = None
    priority: Optional[int] = Field(default=3, ge=1, le=5)
    notes: Optional[str] = None

class TradeItem(BaseModel):
    id: Optional[str] = None
    userId: str
    cardId: str
    quantity: int = Field(default=1, ge=0)
    notes: Optional[str] = None

class Activity(BaseModel):
    id: Optional[str] = None
    userId: str
    type: str
    payload: Optional[Dict[str, Any]] = None
    createdAt: datetime

# Helper input models
class CSVImportPreview(BaseModel):
    rows: int
    issues: List[Dict[str, Any]]
    preview: List[Dict[str, Any]]
