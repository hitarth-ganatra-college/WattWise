"""
FastAPI Backend Server for Predictive Maintenance Platform
==========================================================
Exposes RESTful endpoints for fleet management, telemetry history, 
anomaly scores, financial metrics, and live simulation commands.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pymongo import MongoClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from business_logic.health_index import AssetHealthCalculator
from business_logic.financial_engine import FinancialEngine

app = FastAPI(
    title="Predictive Maintenance REST API",
    description="API layer for Solar & Wind Predictive Maintenance Platform",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper DB Connection
def get_db():
    client = MongoClient(config.MONGO_URI)
    return client[config.DB_NAME]

hc = AssetHealthCalculator()
fe = FinancialEngine()

# --- Pydantic Schemas ---
class AssetCreateSchema(BaseModel):
    asset_id: str = Field(..., example="WT-Nordic-05")
    asset_type: str = Field(..., example="wind_turbine")  # 'wind_turbine' or 'solar_panel'
    region: str = Field(..., example="Nordic")
    capacity_kw: Optional[float] = None
    custom_params: Optional[Dict[str, Any]] = None

class CommandCreateSchema(BaseModel):
    asset_id: str = Field(..., example="WT-Desert-02")
    action: str = Field(..., example="inject_fault")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


# --- REST Endpoints ---

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Predictive Maintenance REST API",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/api/fleet/summary")
def get_fleet_summary():
    """Get top-level KPIs for the entire fleet."""
    db = get_db()
    assets = list(db[config.COLLECTION_ASSETS].find({'status': {'$in': ['active', 'pending']}}))
    
    total_assets = len(assets)
    if total_assets == 0:
        return {
            "total_assets": 0,
            "healthy_count": 0,
            "at_risk_count": 0,
            "healthy_percentage": 100.0,
            "total_daily_revenue_loss": 0.0
        }
        
    telemetry_col = db[config.COLLECTION_TELEMETRY]
    at_risk_count = 0
    total_daily_loss = 0.0
    
    for a in assets:
        doc = telemetry_col.find_one({'asset_id': a['asset_id']}, sort=[('timestamp', -1)])
        if doc:
            scores = doc.get('anomaly_scores', {})
            ahi = hc.calculate_ahi(scores if isinstance(scores, dict) else {})
            if ahi < 50:
                at_risk_count += 1
                
            cap = a.get('capacity_kw', config.WIND_TURBINE_CAPACITY_KW)
            actual = doc.get('active_power') or doc.get('power_output_kw') or 0
            expected = doc.get('expected_power_kw')
            loss_kw = fe.estimate_hourly_power_loss(cap, actual, expected)
            total_daily_loss += fe.estimate_revenue_loss(loss_kw)
            
    healthy_count = total_assets - at_risk_count
    healthy_pct = (healthy_count / total_assets) * 100.0
    
    return {
        "total_assets": total_assets,
        "healthy_count": healthy_count,
        "at_risk_count": at_risk_count,
        "healthy_percentage": round(healthy_pct, 1),
        "total_daily_revenue_loss": round(total_daily_loss, 2)
    }

@app.get("/api/assets")
def get_assets(asset_type: Optional[str] = None, region: Optional[str] = None):
    """List all registered assets with optional filtering."""
    db = get_db()
    query = {'status': {'$in': ['active', 'pending']}}
    if asset_type and asset_type != "All":
        query['asset_type'] = "wind_turbine" if asset_type == "Wind" else "solar_panel" if asset_type == "Solar" else asset_type
    if region and region != "All":
        query['region'] = region
        
    assets = list(db[config.COLLECTION_ASSETS].find(query, {'_id': 0}))
    return {"count": len(assets), "assets": assets}

@app.post("/api/assets", status_code=201)
def create_asset(payload: AssetCreateSchema):
    """Register a new asset into MongoDB for auto-discovery by the simulator."""
    db = get_db()
    col = db[config.COLLECTION_ASSETS]
    
    existing = col.find_one({'asset_id': payload.asset_id})
    if existing:
        raise HTTPException(status_code=400, detail=f"Asset '{payload.asset_id}' already exists.")
        
    cap = payload.capacity_kw
    if cap is None:
        cap = config.WIND_TURBINE_CAPACITY_KW if payload.asset_type == 'wind_turbine' else config.SOLAR_PANEL_CAPACITY_KW
        
    doc = {
        'asset_id': payload.asset_id,
        'asset_type': payload.asset_type,
        'region': payload.region,
        'capacity_kw': cap,
        'custom_params': payload.custom_params or {},
        'status': 'pending',
        'registered_at': datetime.now(timezone.utc)
    }
    col.insert_one(doc)
    return {"message": f"Asset '{payload.asset_id}' created successfully.", "asset": payload.dict()}

@app.get("/api/telemetry/{asset_id}")
def get_asset_telemetry(asset_id: str, limit: int = Query(100, ge=1, le=1000)):
    """Fetch latest telemetry history for a specific asset."""
    db = get_db()
    docs = list(db[config.COLLECTION_TELEMETRY].find({'asset_id': asset_id}, {'_id': 0}).sort('timestamp', -1).limit(limit))
    docs.reverse()
    return {"asset_id": asset_id, "count": len(docs), "history": docs}

@app.get("/api/maintenance/queue")
def get_maintenance_queue():
    """Get prioritized list of maintenance tasks based on Risk Priority Number."""
    db = get_db()
    assets = list(db[config.COLLECTION_ASSETS].find({'status': {'$in': ['active', 'pending']}}))
    telemetry_col = db[config.COLLECTION_TELEMETRY]
    
    queue = []
    for a in assets:
        aid = a['asset_id']
        doc = telemetry_col.find_one({'asset_id': aid}, sort=[('timestamp', -1)])
        if doc:
            scores = doc.get('anomaly_scores', {})
            ahi = hc.calculate_ahi(scores if isinstance(scores, dict) else {})
            cap = a.get('capacity_kw', 1000)
            actual = doc.get('active_power') or doc.get('power_output_kw') or 0
            expected = doc.get('expected_power_kw')
            loss_kw = fe.estimate_hourly_power_loss(cap, actual, expected)
            rev_loss = fe.estimate_revenue_loss(loss_kw)
            
            rec = fe.generate_recommendation(aid, a['asset_type'], ahi, scores if isinstance(scores, dict) else {}, rev_loss)
            rec['region'] = a.get('region', 'Unknown')
            queue.append(rec)
            
    queue.sort(key=lambda x: x['priority_score'], reverse=True)
    return {"count": len(queue), "queue": queue}

@app.post("/api/commands", status_code=201)
def create_command(payload: CommandCreateSchema):
    """Post a dynamic override or fault command for an asset."""
    db = get_db()
    doc = {
        'asset_id': payload.asset_id,
        'action': payload.action,
        'parameters': payload.parameters or {},
        'status': 'pending',
        'created_at': datetime.now(timezone.utc)
    }
    db[config.COLLECTION_COMMANDS].insert_one(doc)
    return {"message": f"Command '{payload.action}' dispatched to '{payload.asset_id}'.", "command": payload.dict()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
