# ULTron Multi-Device Automation - Quick Deploy Guide

## 🚀 Deploy to Replit (FREE, 2 minutes)

### Method 1: One-Click Deploy
1. Go to https://replit.com
2. Click "Import from GitHub"
3. Select `gadelz/ultron-multi-device`
4. Click "Run" → Done!

**Your URL:** https://ultron-multi-device.username.repl.co

### Method 2: Manual Setup
```bash
# Create new Repl
# Language: Python
# Import this repo: https://github.com/gadelz/ultron-multi-device

# In Console, run:
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 🚀 Deploy to Render (FREE)

### One-Click Deploy
1. Create account at https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repo: `gadelz/ultron-multi-device`
4. Settings:
   - Name: `ultron-gateway`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment: `PYTHON=3.11`
5. Click "Create Web Service"

**Your URL:** https://ultron-gateway.onrender.com

---

## 🚀 Deploy to Fly.io (FREE)

### One-Command Deploy
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
cd ultron-multi-device
fly launch --name ultron-gateway --no-deploy
fly volumes create data --size 1
fly deploy
```

**Your URL:** https://ultron-gateway.fly.dev

---

## ✅ Post-Deploy Checklist

```bash
# 1. Test health endpoint
curl https://your-app.onrender.com/health

# 2. Test API key auth
curl -X POST https://your-app.onrender.com/device/register \
  -H "X-API-Key: demo-key-123" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test","flavor":"tasker","host":"127.0.0.1","port":1820}'

# 3. Test broadcast
curl -X POST https://your-app.onrender.com/broadcast \
  -H "X-API-Key: demo-key-123" \
  -H "Content-Type: application/json" \
  -d '{"action":"wake_unlock","payload":{}}'

# 4. List devices
curl https://your-app.onrender.com/devices \
  -H "X-API-Key: demo-key-123"
```

---

## 📱 Update Android Config

### Tasker
1. HTTP Server profile
2. Change port to your service port (default 8080)
3. Path: `/tasker/trigger`
4. Auth: `Authorization: Bearer demo-key-123`

### MacroDroid
1. HTTP Trigger
2. URL: `https://your-app.com/macrodroid/trigger`
3. Same auth header

---

## 💡 Pro Tips

1. **Custom Domain**: Render/Fly both support custom domains
2. **HTTPS**: All platforms provide free SSL
3. **Auto-scaling**: Enable in platform settings
4. **Monitoring**: Use platform's built-in logs

---

## 🔗 Resources

- **GitHub**: https://github.com/gadelz/ultron-multi-device
- **Demo**: https://ultron-demo.gadelz.repl.co
- **Docs**: https://github.com/gadelz/ultron-multi-device/tree/main/docs
