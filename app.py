#!/usr/bin/env python3
"""
ULTron Demo App
Simple demo server with HTML interface
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from gateway.server import app as gateway_app
from schemas.schemas import Command, DeviceAction, DeviceTarget
from models.models import RegisteredDevice, engine, Base
import asyncio

Base.metadata.create_all(engine)

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

# Demo HTML
DEMO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ULTron Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(90deg, #00d9ff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #888; margin-bottom: 30px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .device {
            background: linear-gradient(145deg, #1e3a5f, #0d1b2a);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: transform 0.2s;
        }
        .device:hover { transform: translateY(-5px); }
        .device-icon { font-size: 3rem; margin-bottom: 10px; }
        .device-status { font-size: 0.8rem; color: #00ff88; }
        .device-status.offline { color: #ff4444; }
        button {
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            margin: 5px;
            transition: opacity 0.2s;
        }
        button:hover { opacity: 0.8; }
        button.secondary { background: rgba(255,255,255,0.1); color: #fff; }
        .log {
            background: #0a0a0a;
            border-radius: 8px;
            padding: 16px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            max-height: 300px;
            overflow-y: auto;
            margin-top: 20px;
        }
        .log-entry { margin: 4px 0; padding: 4px 8px; border-radius: 4px; }
        .log-entry.success { color: #00ff88; }
        .log-entry.error { color: #ff4444; }
        .log-entry.info { color: #00d9ff; }
        input, select {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            padding: 12px;
            border-radius: 8px;
            width: 100%;
            margin: 8px 0;
        }
        label { font-size: 0.9rem; color: #aaa; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; margin: 4px; }
        .badge.green { background: rgba(0,255,136,0.2); color: #00ff88; }
        .badge.blue { background: rgba(0,217,255,0.2); color: #00d9ff; }
        .badge.orange { background: rgba(255,170,0,0.2); color: #ffaa00; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ULTron Gateway</h1>
        <p class="subtitle">Multi-Device Voice Automation System</p>
        
        <div class="grid">
            <div class="card">
                <h3>Devices</h3>
                <div id="devices"></div>
            </div>
            
            <div class="card">
                <h3>Quick Actions</h3>
                <button onclick="wakeAll()">Wake All</button>
                <button onclick="playYouTube()">Play YouTube</button>
                <button class="secondary" onclick="registerDemo()">Register Demo</button>
            </div>
            
            <div class="card">
                <h3>Register Device</h3>
                <input type="text" id="deviceId" placeholder="Device ID">
                <select id="flavor">
                    <option value="tasker">Tasker</option>
                    <option value="macrodroid">MacroDroid</option>
                </select>
                <input type="text" id="host" placeholder="Host IP">
                <input type="number" id="port" placeholder="Port" value="1820">
                <button onclick="registerDevice()">Register</button>
            </div>
        </div>
        
        <div class="card">
            <h3>Activity Log</h3>
            <div class="log" id="log"></div>
        </div>
    </div>
    
    <script>
        const API_URL = window.location.origin;
        const API_KEY = 'demo-key-123';
        
        async function request(method, endpoint, body = null) {
            try {
                const options = {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': API_KEY
                    }
                };
                if (body) options.body = JSON.stringify(body);
                const res = await fetch(API_URL + endpoint, options);
                return await res.json();
            } catch (err) {
                log('Error: ' + err.message, 'error');
                return null;
            }
        }
        
        function log(message, type = 'info') {
            const logEl = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = 'log-entry ' + type;
            const time = new Date().toLocaleTimeString();
            entry.textContent = '[' + time + '] ' + message;
            logEl.insertBefore(entry, logEl.firstChild);
        }
        
        async function loadDevices() {
            const devices = await request('GET', '/devices');
            if (devices) {
                document.getElementById('devices').innerHTML = devices.length 
                    ? devices.map(d => '<div class="device">'
                        + '<div class="device-icon">' + (d.flavor === 'tasker' ? 'Phone' : 'Tablet') + '</div>'
                        + '<div>' + (d.label || d.device_id) + '</div>'
                        + '<div class="device-status">' + (d.active ? 'Online' : 'Offline') + '</div>'
                        + '</div>').join('')
                    : '<p style="color:#888">No devices registered</p>';
            }
        }
        
        async function registerDevice() {
            const deviceId = document.getElementById('deviceId').value || 'test_device';
            const flavor = document.getElementById('flavor').value;
            const host = document.getElementById('host').value || '192.168.1.50';
            const port = document.getElementById('port').value || '1820';
            
            const result = await request('POST', '/device/register', {
                device_id: deviceId,
                flavor,
                host,
                port: parseInt(port),
                path: flavor === 'tasker' ? '/tasker/trigger' : '/macrodroid/trigger'
            });
            
            if (result?.ok) {
                log('Device ' + deviceId + ' registered', 'success');
                loadDevices();
            } else {
                log('Failed to register device', 'error');
            }
        }
        
        async function registerDemo() {
            const demoDevices = [
                { device_id: 'main_phone', flavor: 'tasker', host: '192.168.1.50', port: 1820 },
                { device_id: 'secondary_1', flavor: 'macrodroid', host: '192.168.1.51', port: 1880 },
                { device_id: 'secondary_2', flavor: 'macrodroid', host: '192.168.1.52', port: 1880 }
            ];
            
            for (const device of demoDevices) {
                await request('POST', '/device/register', device);
            }
            log('Demo devices registered!', 'success');
            loadDevices();
        }
        
        async function wakeAll() {
            const result = await request('POST', '/broadcast', {
                action: 'wake_unlock',
                payload: {}
            });
            log('Woke all devices', 'info');
        }
        
        async function playYouTube() {
            const result = await request('POST', '/broadcast', {
                action: 'play_media',
                payload: { app: 'com.google.android.youtube' }
            });
            log('YouTube launched on all devices', 'info');
        }
        
        loadDevices();
        log('ULTron Gateway loaded', 'success');
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def demo():
    return DEMO_HTML

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ultron-gateway", "version": "0.1.0", "demo": True}
