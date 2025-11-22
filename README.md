# Gotta Track 'Em

This is a scaffold for a PWA that tracks Pokémon TCG collections with scan‑to‑add, live pricing, and offline support.

Quick start:
- Backend exposes catalog, pricing (mock), scan identify (mock), and collection endpoints backed by MongoDB.
- Frontend is a Vite + React PWA scaffold with service worker and manifest.

Environment variables (.env.example):

```
# Backend
DATABASE_URL=
DATABASE_NAME=
POKEMON_TCG_API_KEY=
TCGPLAYER_PUBLIC_KEY=
TCGPLAYER_PRIVATE_KEY=
USE_MOCK_ADAPTERS=true

# Frontend
VITE_BACKEND_URL=
```

