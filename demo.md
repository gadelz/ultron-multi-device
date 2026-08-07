# ULTron Multi-Device Automation - Demo

## 🎯 Live Demo

**Try it now:** https://ultron-demo.gadelz.repl.co

> **Note:** This is a demo instance with limited functionality. For full features, deploy your own instance.

---

## ⚡ Quick Actions

1. **Wake All Devices** - Send wake command to all registered devices
2. **Play YouTube** - Launch YouTube on all devices
3. **Register Demo** - Add sample devices to test with

---

## 📱 Connect Your Devices

### For Tasker Users
```
POST /device/register
{
  "device_id": "main_phone",
  "flavor": "tasker",
  "host": "192.168.1.50",
  "port": 1820,
  "path": "/tasker/trigger"
}
```

### For MacroDroid Users
```
POST /device/register
{
  "device_id": "secondary_1",
  "flavor": "macrodroid",
  "host": "192.168.1.51",
  "port": 1880,
  "path": "/macrodroid/trigger"
}
```

---

## 🔧 Self-Host

Want your own instance?

```bash
git clone https://github.com/gadelz/ultron-multi-device.git
cd ultron-multi-device
pip install -r requirements.txt
uvicorn main:app --port 8080
```

See [DEPLOY.md](DEPLOY.md) for cloud deployment options.

---

## 📊 Demo Features

- ✅ Device registration
- ✅ Wake all devices
- ✅ Play YouTube broadcast
- ✅ Activity logging
- ✅ API key authentication
- ❌ No LLM integration (demo mode)
- ❌ No persistent database (in-memory)
- ❌ No device connectivity (simulation only)

---

**Built by [gadelz](https://github.com/gadelz)**
