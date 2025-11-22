"""
Adapters with interface contracts and mock implementations with feature flags.
"""
from __future__ import annotations
import os
import time
import random
from typing import List, Dict, Any, Optional
import requests

POKEMON_TCG_API_BASE = "https://api.pokemontcg.io/v2"

USE_MOCKS = os.getenv("USE_MOCK_ADAPTERS", "true").lower() in ("1","true","yes")

class PokemonTCGAdapter:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("POKEMON_TCG_API_KEY")

    def _headers(self):
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        return headers

    def list_sets(self, page: int = 1, pageSize: int = 250) -> Dict[str, Any]:
        if USE_MOCKS:
            return {
                "data": [
                    {"id": "base1", "name": "Base Set", "series": "Base", "total": 102, "printedTotal": 102, "releaseDate": "1999/01/09", "legalities": {"standard": "not_legal", "expanded": "not_legal"}},
                    {"id": "sv1", "name": "Scarlet & Violet", "series": "Scarlet & Violet", "total": 258, "printedTotal": 258, "releaseDate": "2023/03/31", "legalities": {"standard": "legal", "expanded": "legal"}},
                ]
            }
        resp = requests.get(f"{POKEMON_TCG_API_BASE}/sets", params={"page": page, "pageSize": pageSize}, headers=self._headers(), timeout=20)
        resp.raise_for_status()
        return resp.json()

    def search_cards(self, q: str, page: int = 1, pageSize: int = 50) -> Dict[str, Any]:
        if USE_MOCKS:
            # Very small mock list
            sample = [
                {"id": "base1-4", "name": "Charizard", "set": {"id": "base1", "name": "Base Set"}, "number": "4", "rarity": "Rare Holo", "images": {"small": "https://images.pokemontcg.io/base1/4.png", "large": "https://images.pokemontcg.io/base1/4_hires.png"}, "variants": {"normal": False, "holo": True}},
                {"id": "sv1-12", "name": "Sprigatito", "set": {"id": "sv1", "name": "Scarlet & Violet"}, "number": "12", "rarity": "Common", "images": {"small": "https://images.pokemontcg.io/sv1/12.png", "large": "https://images.pokemontcg.io/sv1/12_hires.png"}, "variants": {"normal": True, "reverse": True}},
            ]
            return {"data": [c for c in sample if q.lower() in c["name"].lower() or q.lower() in c.get("set",{}).get("id","" ).lower()]}
        resp = requests.get(f"{POKEMON_TCG_API_BASE}/cards", params={"q": q, "page": page, "pageSize": pageSize}, headers=self._headers(), timeout=20)
        resp.raise_for_status()
        return resp.json()

class TCGPlayerAdapter:
    TOKEN_URL = "https://api.tcgplayer.com/token"
    API_BASE = "https://api.tcgplayer.com/pricing"

    def __init__(self, public_key: Optional[str] = None, private_key: Optional[str] = None):
        self.public_key = public_key or os.getenv("TCGPLAYER_PUBLIC_KEY")
        self.private_key = private_key or os.getenv("TCGPLAYER_PRIVATE_KEY")
        self._token: Optional[Dict[str, Any]] = None

    def _get_token(self) -> Optional[str]:
        if USE_MOCKS:
            return "mock-token"
        if self._token and time.time() < self._token.get("expires_at", 0):
            return self._token.get("access_token")
        data = {
            "grant_type": "client_credentials",
            "client_id": self.public_key,
            "client_secret": self.private_key,
        }
        resp = requests.post(self.TOKEN_URL, data=data, timeout=20)
        resp.raise_for_status()
        tok = resp.json()
        tok["expires_at"] = time.time() + tok.get("expires_in", 3600) - 60
        self._token = tok
        return tok.get("access_token")

    def get_prices_for_products(self, product_ids: List[int]) -> Dict[str, Any]:
        if USE_MOCKS:
            out = {}
            for pid in product_ids:
                out[str(pid)] = {
                    "market": round(random.uniform(1, 500), 2),
                    "low": round(random.uniform(1, 400), 2),
                    "mid": round(random.uniform(1, 450), 2),
                    "high": round(random.uniform(1, 600), 2),
                    "timestamp": int(time.time()),
                    "source": "TCGplayer"
                }
            return out
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        resp = requests.get(f"{self.API_BASE}/product/{','.join(map(str,product_ids))}", headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json()

class OCRAdapter:
    def extract(self, image_bytes: bytes) -> Dict[str, Any]:
        # Mock OCR returns random plausible values
        return {"number": "4", "setHint": "base1", "confidence": 0.62}

class ImageMatchAdapter:
    def similar(self, image_bytes: bytes, top_k: int = 5) -> List[Dict[str, Any]]:
        # Mock image match with placeholder candidates
        return [
            {"cardId": "base1-4", "score": 0.88},
            {"cardId": "base1-3", "score": 0.76},
        ]
