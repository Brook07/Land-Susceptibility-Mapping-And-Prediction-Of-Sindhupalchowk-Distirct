# Minimal FastAPI backend for GeoShield

This directory contains a minimal FastAPI app that exposes model/data artifacts as simple JSON endpoints for the frontend.

Endpoints
- `GET /api/health` — basic health check
- `GET /api/analysis/hotspots` — returns the GeoJSON found at `data/processed/inventory/landslides_epsg4326.geojson`
- `GET /api/analysis/summary` — lightweight KPIs derived from the GeoJSON (counts, average risk)
- `POST /api/analysis/simulation` — accepts simulation parameters and returns features with `simulated_risk`

Run locally

1. Create and activate a Python venv and install deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the server:

```powershell
uvicorn backend.main:app --reload --port 8000
```

The frontend can call `http://localhost:8000/api/analysis/hotspots` (CORS allowed for localhost).
