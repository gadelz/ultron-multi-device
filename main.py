from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gateway.server import app as gateway_app
from schemas.schemas import Command, DeviceAction, DeviceTarget
from models.models import RegisteredDevice, engine, Base

# Create DB tables
Base.metadata.create_all(engine)

# Main app
app = FastAPI(title="ULTron Demo", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include gateway routes
app.include_router(gateway_app.router, prefix="")

# Serve demo HTML
@app.get("/", response_class=HTMLResponse)
async def demo():
    with open("app.py.html", "r") as f:
        return f.read()

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ultron-gateway", "version": "0.1.0"}
