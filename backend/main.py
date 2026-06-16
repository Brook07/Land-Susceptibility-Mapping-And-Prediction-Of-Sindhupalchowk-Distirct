from pathlib import Path
from typing import Any, Dict, List
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="GeoShield Minimal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[1]
GEOJSON_PATH = ROOT / "data" / "processed" / "inventory" / "landslides_epsg4326.geojson"

def load_geojson() -> Dict[str, Any]:
    if not GEOJSON_PATH.exists():
        raise FileNotFoundError(str(GEOJSON_PATH))
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/analysis/hotspots")
def get_hotspots():
    try:
        gj = load_geojson()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="GeoJSON not found")
    return gj


@app.get("/api/analysis/summary")
def get_summary():
    try:
        gj = load_geojson()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="GeoJSON not found")

    features = gj.get("features", []) if isinstance(gj, dict) else []
    total = len(features)

    risks: List[float] = []
    critical = 0
    for f in features:
        props = f.get("properties", {}) if isinstance(f, dict) else {}
        r = props.get("risk")
        if isinstance(r, (int, float)):
            risks.append(float(r))
        sev = str(props.get("severity", "")).lower()
        if sev == "critical":
            critical += 1

    avg_risk = sum(risks) / len(risks) if risks else None
    high_risk_count = sum(1 for r in risks if r > 0.8)

    return {
        "total_hotspots": total,
        "critical_hotspots": critical,
        "high_risk_count": high_risk_count,
        "average_risk": avg_risk,
        "population_exposed": None,
        "environmental_health_index": None,
    }


class SimulationParams(BaseModel):
    rainfall: float = 0.0
    vegetation: float = 0.0
    roadExpansion: float = 0.0
    riverErosion: float = 0.0


@app.post("/api/analysis/simulation")
def simulate(params: SimulationParams):
    try:
        gj = load_geojson()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="GeoJSON not found")

    risk_multiplier = (
        1
        + (params.rainfall * 0.5) / 100
        + (params.roadExpansion * 0.4) / 100
        - (params.vegetation * 0.3) / 100
        + (params.riverErosion * 0.35) / 100
    )

    features = gj.get("features", []) if isinstance(gj, dict) else []
    simulated: List[Dict[str, Any]] = []
    for f in features:
        newf = dict(f)
        props = dict(newf.get("properties", {}))
        r = props.get("risk")
        if isinstance(r, (int, float)):
            props["simulated_risk"] = min(1.0, float(r) * risk_multiplier)
        else:
            props["simulated_risk"] = None
        newf["properties"] = props
        simulated.append(newf)

    return {"risk_multiplier": risk_multiplier, "features": simulated}
