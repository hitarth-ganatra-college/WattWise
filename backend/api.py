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
import io
import base64
import pyotp
import qrcode

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from business_logic.health_index import AssetHealthCalculator
from business_logic.financial_engine import FinancialEngine

def generate_totp_qr(email: str, secret: str) -> tuple:
    """Generate TOTP provisioning URI and base64 PNG data URL for scanning."""
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=email, issuer_name="WattWise")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    qr_code_base64 = f"data:image/png;base64,{img_str}"
    
    return provisioning_uri, qr_code_base64

app = FastAPI(
    title="Predictive Maintenance REST API",
    description="API layer for Solar & Wind Predictive Maintenance Platform with Mandatory 2FA TOTP Auth",
    version="2.1.0"
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

class RegisterSchema(BaseModel):
    name: str = Field(..., example="Alex Morgan")
    email: str = Field(..., example="alex@powercorp.com")
    password: str = Field(...)
    app_password: Optional[str] = Field(default="", example="")
    role: Optional[str] = Field(default="Operator", example="Fleet Operator")

class Verify2FASchema(BaseModel):
    email: str = Field(..., example="alex@powercorp.com")
    totp_code: str = Field(..., example="123456")

class LoginSchema(BaseModel):
    email: str = Field(..., example="alex@powercorp.com")
    password: str = Field(...)
    totp_code: Optional[str] = Field(default=None, example="123456")

class ContactSchema(BaseModel):
    name: str = Field(..., example="Alex Morgan")
    email: str = Field(..., example="alex@powercorp.com")
    organization: Optional[str] = Field(default="", example="Horizon Power")
    asset_type: Optional[str] = Field(default="Hybrid Wind & Solar Portfolio")
    fleet_capacity: Optional[str] = Field(default="50 MW - 250 MW")
    notes: Optional[str] = Field(default="")

class ProfileUpdateSchema(BaseModel):
    email: str = Field(..., example="alex@powercorp.com")
    name: Optional[str] = None
    phone: Optional[str] = None
    app_password: Optional[str] = None


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
            ahi = doc.get('ahi') if (doc.get('ahi') is not None) else hc.calculate_ahi(scores if isinstance(scores, dict) else {})
            if ahi < 80:
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
    """List all registered assets with optional filtering, attached GPS coordinates, and health indices."""
    db = get_db()
    query = {'status': {'$in': ['active', 'pending']}}
    if asset_type and asset_type != "All":
        query['asset_type'] = "wind_turbine" if asset_type == "Wind" else "solar_panel" if asset_type == "Solar" else asset_type
    if region and region != "All":
        query['region'] = region
        
    assets = list(db[config.COLLECTION_ASSETS].find(query, {'_id': 0}))
    telemetry_col = db[config.COLLECTION_TELEMETRY]
    
    enriched = []
    for a in assets:
        reg_info = config.REGIONAL_MODIFIERS.get(a.get('region', 'Temperate'), config.REGIONAL_MODIFIERS['Temperate'])
        a['lat'] = a.get('lat') or reg_info.get('lat', 51.1657)
        a['lon'] = a.get('lon') or reg_info.get('lon', 10.4515)
        a['oem'] = a.get('oem') or (reg_info.get('oem_wind') if a.get('asset_type') == 'wind_turbine' else reg_info.get('oem_solar'))
        
        latest_doc = telemetry_col.find_one({'asset_id': a['asset_id']}, sort=[('timestamp', -1)])
        if latest_doc:
            scores = latest_doc.get('anomaly_scores', {})
            ahi = latest_doc.get('ahi') if (latest_doc.get('ahi') is not None) else hc.calculate_ahi(scores if isinstance(scores, dict) else {})
            a['ahi'] = round(float(ahi), 1)
            a['active_power'] = latest_doc.get('active_power') or latest_doc.get('power_output_kw') or 0
            a['expected_power'] = latest_doc.get('expected_power_kw') or 0
        else:
            a['ahi'] = float(a.get('ahi', 100.0))
            a['active_power'] = 0
            a['expected_power'] = 0
            
        a['health_status'] = hc.classify_health(a['ahi'])
        enriched.append(a)

    return {"count": len(enriched), "assets": enriched}

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

@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterSchema):
    """Register user with compulsory 2FA TOTP setup and return base64 QR Code."""
    db = get_db()
    email = payload.email.strip().lower()
    users_col = db['users']
    existing = users_col.find_one({'email': email})
    if existing:
        raise HTTPException(status_code=400, detail=f"Account with email '{email}' already exists.")

    name = payload.name.strip() or email.split('@')[0].capitalize()
    totp_secret = pyotp.random_base32()
    totp_uri, qr_code_base64 = generate_totp_qr(email, totp_secret)

    doc = {
        'name': name,
        'email': email,
        'password': payload.password,
        'app_password': payload.app_password or '',
        'role': payload.role or 'Admin',
        'totp_secret': totp_secret,
        'totp_verified': False,
        'created_at': datetime.now(timezone.utc)
    }
    users_col.insert_one(doc)

    # Sync with settings for alert notifications
    email_cfg = {
        'key': 'email_config',
        'recipient_email': email,
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': email,
        'smtp_pass': payload.app_password or '',
        'updated_at': datetime.now(timezone.utc)
    }
    db['settings'].update_one({'key': 'email_config'}, {'$set': email_cfg}, upsert=True)

    return {
        "message": f"Welcome to WattWise, {name}! 2FA is mandatory. Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.).",
        "user": {
            "name": name,
            "email": email,
            "role": doc['role'],
            "totp_verified": False
        },
        "totp_secret": totp_secret,
        "totp_uri": totp_uri,
        "qr_code_base64": qr_code_base64
    }

@app.post("/api/auth/verify-2fa")
def verify_2fa(payload: Verify2FASchema):
    """Verify 6-digit TOTP code for a user and mark 2FA verified."""
    db = get_db()
    email = payload.email.strip().lower()
    users_col = db['users']
    user = users_col.find_one({'email': email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    totp_secret = user.get('totp_secret')
    if not totp_secret:
        raise HTTPException(status_code=400, detail="2FA is not set up for this user.")

    totp = pyotp.TOTP(totp_secret)
    if not totp.verify(payload.totp_code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid 6-digit TOTP authentication code.")

    # Mark 2FA as completed/verified in MongoDB
    users_col.update_one({'email': email}, {'$set': {'totp_verified': True}})

    return {
        "status": "success",
        "message": "2FA TOTP code verified successfully.",
        "email": email
    }

@app.post("/api/auth/login")
def login(payload: LoginSchema):
    """Authenticate user with email, password, and mandatory 2FA TOTP code."""
    db = get_db()
    email = payload.email.strip().lower()
    users_col = db['users']
    user = users_col.find_one({'email': email})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if user.get('password') != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    totp_secret = user.get('totp_secret')
    totp_verified = (user.get('totp_verified') is True)
    
    # If 2FA has NOT been verified by this user yet (old/unverified user)
    if not totp_verified:
        if not totp_secret:
            totp_secret = pyotp.random_base32()
            users_col.update_one({'email': email}, {'$set': {'totp_secret': totp_secret, 'totp_verified': False}})
            
        totp_uri, qr_code_base64 = generate_totp_qr(email, totp_secret)
        
        if payload.totp_code:
            totp = pyotp.TOTP(totp_secret)
            if not totp.verify(payload.totp_code, valid_window=1):
                raise HTTPException(status_code=401, detail="Invalid 6-digit TOTP authentication code.")
            
            # Mark verified in MongoDB
            users_col.update_one({'email': email}, {'$set': {'totp_verified': True}})
            return {
                "message": f"2FA setup complete! Welcome back, {user.get('name', email)}!",
                "user": {
                    "name": user.get('name', email),
                    "email": user.get('email'),
                    "role": user.get('role', 'Admin'),
                    "app_password": user.get('app_password', ''),
                    "totp_verified": True
                }
            }

        return {
            "status": "2fa_setup_required",
            "message": "2FA setup is required for your account. Scan the QR Code below and enter the 6-digit code.",
            "email": email,
            "totp_secret": totp_secret,
            "totp_uri": totp_uri,
            "qr_code_base64": qr_code_base64
        }

    # If user ALREADY has verified 2FA setup:
    if not payload.totp_code:
        return {
            "status": "2fa_required",
            "message": "2FA code required. Please enter 6-digit code from your authenticator app.",
            "email": email
        }

    totp = pyotp.TOTP(totp_secret)
    if not totp.verify(payload.totp_code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid 6-digit TOTP authentication code.")

    return {
        "message": f"Welcome back, {user.get('name', email)}!",
        "user": {
            "name": user.get('name', email),
            "email": user.get('email'),
            "role": user.get('role', 'Admin'),
            "app_password": user.get('app_password', ''),
            "phone": user.get('phone', ''),
            "totp_verified": True
        }
    }


@app.put("/api/auth/profile")
def update_profile(payload: ProfileUpdateSchema):
    """Update user profile info (name, phone, Gmail app_password)."""
    db = get_db()
    email = payload.email.strip().lower()
    users_col = db['users']
    user = users_col.find_one({'email': email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    update_data = {}
    if payload.name is not None:
        update_data['name'] = payload.name.strip()
    if payload.phone is not None:
        update_data['phone'] = payload.phone.strip()
    if payload.app_password is not None:
        update_data['app_password'] = payload.app_password.strip()

    if update_data:
        users_col.update_one({'email': email}, {'$set': update_data})

        # Sync app_password to MongoDB settings for email alerts if provided
        if payload.app_password is not None:
            email_cfg = {
                'key': 'email_config',
                'recipient_email': email,
                'smtp_host': 'smtp.gmail.com',
                'smtp_port': 587,
                'smtp_user': email,
                'smtp_pass': payload.app_password.strip(),
                'updated_at': datetime.now(timezone.utc)
            }
            db['settings'].update_one({'key': 'email_config'}, {'$set': email_cfg}, upsert=True)

    updated_user = users_col.find_one({'email': email})
    return {
        "message": "Profile updated successfully.",
        "user": {
            "name": updated_user.get('name', ''),
            "email": updated_user.get('email', ''),
            "role": updated_user.get('role', 'Admin'),
            "app_password": updated_user.get('app_password', ''),
            "phone": updated_user.get('phone', ''),
            "totp_verified": updated_user.get('totp_verified', True)
        }
    }


@app.post("/api/contact")
def submit_contact_audit(payload: ContactSchema):
    """Submit B2B SCADA technical audit request."""
    db = get_db()
    doc = {
        'name': payload.name,
        'email': payload.email,
        'organization': payload.organization,
        'asset_type': payload.asset_type,
        'fleet_capacity': payload.fleet_capacity,
        'notes': payload.notes,
        'created_at': datetime.now(timezone.utc)
    }
    db['contact_requests'].insert_one(doc)
    return {
        "status": "success",
        "message": f"Request received for {payload.name}! Our engineering team will contact {payload.email} within 2 hours."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
