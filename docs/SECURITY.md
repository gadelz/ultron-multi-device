# ULTron Security Configuration Guide

## 🔒 Current Security Measures

### 1. API Key Authentication
- **Gateway**: `X-API-Key` header validation
- **Devices**: Bearer token authentication
- **Default**: `changeme-secret-key` (MUST CHANGE)

### 2. Input Validation
- Pydantic model validation for all requests
- Type checking and pattern matching
- Payload size limits (1MB default)

### 3. Request Logging
- All requests logged to stdout
- Audit trail for device actions
- IP address tracking

### 4. Database Security
- SQLite with connection pooling
- Query parameterization (prevents SQL injection)
- No hardcoded credentials

## ⚠️ Security Risks & Fixes

### Critical Issues

#### 1. Hardcoded API Key
```bash
# CURRENT (INSECURE)
API_KEY = os.getenv("ULTRON_API_KEY", "changeme-secret-key")

# FIX: Use strong random key
ULTRON_API_KEY=$(openssl rand -hex 32)
echo "ULTRON_API_KEY=$ULTRON_API_KEY" >> .env
```

#### 2. HTTP Instead of HTTPS
```bash
# CURRENT (INSECURE on public networks)
http://192.168.1.50:1820

# FIX: Use HTTPS or VPN
https://192.168.1.50:1820
# Or use SSH tunnel
ssh -L 1820:localhost:1820 user@server
```

#### 3. No Rate Limiting
```bash
# ADD in server.py
from src.gateway.security import SecurityMiddleware

# Configure rate limiting
config = {
    "rate_limit_enabled": True,
    "rate_limit_window": 60,  # seconds
    "rate_limit_max": 60,     # requests per window
    "ip_whitelist": ["192.168.1.0/24"],  # only local network
}
app.add_middleware(SecurityMiddleware, config=config)
```

### High Priority Issues

#### 4. CORS Wildcard
```bash
# CURRENT (INSECURE)
allow_origins=["*"]

# FIX: Restrict to known origins
allow_origins=["http://localhost:3000", "https://your-domain.com"]
```

#### 5. No HTTPS for Device Communication
```bash
# FIX: Generate self-signed cert
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Use in Tasker/MacroDroid
https://192.168.1.50:8443/trigger
```

#### 6. Device Token Storage
```bash
# CURRENT: Plain text tokens in database
# FIX: Hash tokens before storage
from src.gateway.auth import AuthService

auth = AuthService()
hashed_token = auth.hash_password(token)
device.auth_token = hashed_token
```

## 🛡️ Production Security Checklist

### Before Deployment
- [ ] Change all default passwords and API keys
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall rules (allow only necessary ports)
- [ ] Set up VPN for remote access
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set up logging and monitoring
- [ ] Test with security scanner (OWASP ZAP)

### Network Security
```bash
# Firewall rules (ufw)
sudo ufw allow from 192.168.1.0/24 to any port 8080
sudo ufw allow from 192.168.1.0/24 to any port 1820
sudo ufw deny 8080
sudo ufw deny 1820

# Only allow local network
```

### Docker Security
```yaml
# docker-compose.yml additions
services:
  gateway:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    volumes:
      - ./data:/app/data:rw
      - ./logs:/app/logs:rw
```

### Device Security
1. **Use unique tokens per device**
2. **Enable HTTPS in Tasker/MacroDroid**
3. **Rotate tokens quarterly**
4. **Remove unused devices**

## 🔍 Security Testing

### Penetration Testing
```bash
# Test API key bypass
curl http://localhost:8080/health

# Test with invalid key
curl -X POST http://localhost:8080/webhook \
  -H "X-API-Key: wrong-key" \
  -H "Content-Type: application/json" \
  -d '{"intent":"wake_all"}'

# Test rate limiting
for i in {1..100}; do
  curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:8080/webhook \
    -H "X-API-Key: your-key" \
    -H "Content-Type: application/json" \
    -d '{"intent":"wake_all"}'
  echo
done
# Should get 429 after 60 requests
```

### OWASP Top 10 Checklist
- [ ] **A01: Broken Access Control** - API key validation working
- [ ] **A02: Cryptographic Failures** - Tokens hashed, HTTPS used
- [ ] **A03: Injection** - Parameterized queries, input validation
- [ ] **A04: Insecure Design** - Defense in depth applied
- [ ] **A05: Security Misconfiguration** - Hardened defaults
- [ ] **A06: Vulnerable Components** - Dependencies updated
- [ ] **A07: Auth Failures** - Rate limiting, token expiry
- [ ] **A08: Software Integrity** - Code signing (optional)
- [ ] **A09: Logging Failures** - Audit trail implemented
- [ ] **A10: SSRF** - URL validation for device endpoints

## 📋 Incident Response

### If Compromised
1. **Immediately**: Revoke all device tokens
2. **Rotate**: API keys and secrets
3. **Audit**: Check logs for unauthorized access
4. **Notify**: Alert affected users
5. **Patch**: Fix vulnerability
6. **Restore**: From clean backup

```bash
# Revoke all tokens
python -c "
import sys; sys.path.insert(0, 'src')
from gateway.auth import AuthService
auth = AuthService()
# Revoke all tokens
auth.tokens.clear()
print('All tokens revoked')
"
```
