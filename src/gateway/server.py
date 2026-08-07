import os, sys, json, logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from datetime import datetime
import httpx, asyncio

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from models.models import RegisteredDevice, ExecutionLog
from schemas.schemas import Command, DeviceAction, IntentParseRequest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
app = FastAPI(title="ULTron Gateway", version="0.1.0")
logger = logging.getLogger("ultron-gateway")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ---------------------------------------------------------------------------
# Database Setup
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ultron.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = __import__("models.models", fromlist=["Base"]).Base
Base.metadata.create_all(engine)

API_KEY = os.getenv("ULTron_API_KEY", "changeme-secret-key")

# ---------------------------------------------------------------------------
# Auth Dependency
# ---------------------------------------------------------------------------
async def verify_key(x_api_key: Optional[str] = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True

# ---------------------------------------------------------------------------
# Intake Models
# ---------------------------------------------------------------------------
class DeviceRegister(BaseModel):
    device_id: str
    label: Optional[str] = None
    flavor: str = Field(..., regex="^(tasker|macrodroid)$")
    host: str
    port: int = 8080
    path: str = "/"
    auth_token: Optional[str] = None

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.post("/device/register")
async def register_device(body: DeviceRegister, _: bool = Depends(verify_key)):
    db = SessionLocal()
    try:
        dev = db.query(RegisteredDevice).filter(RegisteredDevice.device_id == body.device_id).first()
        if dev:
            dev.label = body.label
            dev.flavor = body.flavor
            dev.host = body.host
            dev.port = body.port
            dev.path = body.path
            dev.auth_token = body.auth_token
            dev.active = True
        else:
            dev = RegisteredDevice(**body.dict())
            db.add(dev)
        db.commit()
        return {"ok": True, "device_id": body.device_id}
    finally:
        db.close()

@app.post("/webhook")
async def ingest_from_ai_core(cmd: Command, _: bool = Depends(verify_key)):
    """
    Primary intake from AI Core (LLM / Whisper parsed intent).
    Dispatches actions across target devices concurrently with per-device delay.
    """
    db = SessionLocal()
    jobs = []
    try:
        for t in cmd.targets:
            jobs.append(_schedule_target(db, cmd, t))
        results = await asyncio.gather(*jobs, return_exceptions=True)
        return {"correlate_id": cmd.correlate_id, "results": results}
    finally:
        db.close()

@app.post("/broadcast")
async def broadcast_action(action: DeviceAction, payload: Optional[dict] = None,
                          _: bool = Depends(verify_key)):
    """
    Fire single action to ALL active registered targets (convenience endpoint).
    """
    db = SessionLocal()
    devices = db.query(RegisteredDevice).filter(RegisteredDevice.active == True).all()
    payload = payload or {}
    jobs = [
        _fire(dev, DeviceAction(action), payload, 0)
        for dev in devices
    ]
    results = await asyncio.gather(*jobs, return_exceptions=True)
    return {"action": action.value, "results": results}

@app.get("/devices")
async def list_devices(_: bool = Depends(verify_key)):
    db = SessionLocal()
    devices = db.query(RegisteredDevice).all()
    return [{
        "device_id": d.device_id,
        "label": d.label,
        "flavor": d.flavor,
        "host": d.host,
        "port": d.port,
        "active": d.active,
    } for d in devices]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _schedule_target(db, cmd: Command, target):
    dev = db.query(RegisteredDevice).filter(RegisteredDevice.device_id == target.device_id).first()
    if not dev:
        return {"device_id": target.device_id, "error": "unknown device"}
    # annotate log pre-attempt
    log = ExecutionLog(
        correlate_id=cmd.correlate_id,
        device_id=target.device_id,
        action=target.action.value,
        status="scheduled",
        response=None,
    )
    db.add(log); db.commit()
    if target.delay_ms:
        await asyncio.sleep(target.delay_ms / 1000.0)
    return await _fire(dev, target.action, target.payload, log.id)

async def _fire(dev: RegisteredDevice, action: DeviceAction, payload: dict, log_id: int):
    url = f"http://{dev.host}:{dev.port}{dev.path}"
    headers = {}
    if dev.auth_token:
        headers["Authorization"] = f"Bearer {dev.auth_token}"

    # normalize payload
    body = {"action": action.value, "payload": payload}

    try:
        async with httpx.AsyncClient(timeout=8.0) as c:
            r = await c.post(url, json=body, headers=headers)
        result = r.json()
        status = "ok" if r.status_code == 200 else "error"
    except Exception as e:
        result = {"error": str(e)}
        status = "error"

    # update log
    db = SessionLocal()
    try:
        log = db.query(ExecutionLog).filter(ExecutionLog.id == log_id).first()
        if log:
            log.status = status
            log.response = json.dumps(result)
            db.commit()
    finally:
        db.close()
    return {"device_id": dev.device_id, "status": status, "result": result}
