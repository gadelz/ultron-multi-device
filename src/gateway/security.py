"""
Security middleware for ULTron Gateway
Implements rate limiting, CORS, request logging, and IP filtering
"""
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Dict, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import hashlib

logger = logging.getLogger("ultron-security")

# Rate limiting storage
rate_limits: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 60     # requests per window

class SecurityMiddleware:
    """Security middleware for ULTron Gateway"""
    
    def __init__(self, app: FastAPI, config: dict):
        self.app = app
        self.config = config
        self.allowed_origins = config.get("cors_origins", ["*"])
        self.rate_limit_enabled = config.get("rate_limit_enabled", True)
        self.ip_whitelist = config.get("ip_whitelist", [])
        self.max_payload_size = config.get("max_payload_size", 1024 * 1024)  # 1MB
        
    async def __call__(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(f"[{client_ip}] {request.method} {request.url.path}")
        
        # IP whitelist check
        if self.ip_whitelist and client_ip not in self.ip_whitelist:
            logger.warning(f"Blocked IP: {client_ip}")
            raise HTTPException(status_code=403, detail="IP not allowed")
        
        # Rate limiting
        if self.rate_limit_enabled:
            now = time.time()
            # Clean old entries
            rate_limits[client_ip] = [t for t in rate_limits[client_ip] if now - t < RATE_LIMIT_WINDOW]
            if len(rate_limits[client_ip]) >= RATE_LIMIT_MAX:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                raise HTTPException(status_code=429, detail="Too many requests")
            rate_limits[client_ip].append(now)
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            return response
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

def setup_security(app: FastAPI, config: dict):
    """Setup security middleware and headers"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if config.get("allow_all_origins", False) else config.get("cors_origins", []),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    if config.get("trusted_hosts"):
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=config.get("trusted_hosts", [])
        )
    
    # Security headers
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
    
    # Request size limit
    @app.middleware("http")
    async def request_size_limit(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > config.get("max_payload_size", 1024 * 1024):
            raise HTTPException(status_code=413, detail="Payload too large")
        return await call_next(request)
    
    # Audit logging
    @app.middleware("http")
    async def audit_logger(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(f"Audit: {request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)")
        return response
