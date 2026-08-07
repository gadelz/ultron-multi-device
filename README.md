# ULTron Multi-Device Automation

> **AI-powered multi-device orchestration system** — control Android phones, tablets, and other devices via voice commands or API. Built with FastAPI, Ollama (local LLM), and Tasker/MacroDroid.

## 🚀 Live Demo

🎯 **Try it now:** https://ultron-demo.gadelz.repl.co

> Note: Demo has limited functionality (no real device connection, SQLite in-memory)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ULTron Multi-Device System                       │
└─────────────────────────────────────────────────────────────────────────┘

[User Voice/Text] → [LLM Parser] → [Gateway API :8080] → [Android Devices]
                              ↓
                    [Keyword Fallback]
```

**Components:**
- **AI Core**: Parses voice/text commands into structured device actions
- **Gateway API**: FastAPI server that orchestrates device commands
- **Android Clients**: Tasker (main phone) + MacroDroid (secondary phones)
- **Database**: SQLite for device registry and execution logs

---

## ⚡ Quick Start

### Deploy Your Own (Free)

```bash
# 1. Clone repo
git clone https://github.com/gadelz/ultron-multi-device.git
cd ultron-multi-device

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run locally
uvicorn main:app --port 8080 --reload

# 4. Open demo
open http://localhost:8080
```

### Deploy to Render (Free Tier)

```bash
# Connect your GitHub repo to Render
# Service Type: Web Service
# Build Command: pip install -r requirements.txt
# Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Get free URL: `https://your-app.onrender.com`

---

## 🎮 Demo Features

1. **Register Devices** — Add Tasker/MacroDroid devices
2. **Wake All** — Send wake command to all registered devices
3. **Play YouTube** — Launch YouTube on all devices
4. **Activity Log** — See all actions in real-time

---

## 📱 Android Setup

### Tasker (Primary Phone)
1. Import profile from `android/tasker/`
2. Set HTTP port to 1820
3. Path: `/tasker/trigger`
4. Auth: `Authorization: Bearer [token]`

### MacroDroid (Secondary Devices)
1. Trigger: HTTP Server → POST `/macrodroid/trigger:1880`
2. Actions: Screen On → Dismiss Keyguard → Launch YouTube

---

## 🧠 LLM Integration

- **Ollama** (local, free) — llama3.2, mistral
- **OpenAI** (cloud) — gpt-4o, gpt-4o-mini
- **Fallback parser** (no LLM needed)

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Gateway health |
| POST | `/webhook` | Dispatch to devices |
| POST | `/broadcast` | Action to all devices |
| POST | `/device/register` | Register device |
| GET | `/devices` | List devices |

---

## 📁 Project Structure

```
ultron-multi-device/
├── src/
│   ├── gateway/server.py    # FastAPI gateway
│   ├── llm/core.py          # LLM client
│   ├── schemas/             # Pydantic models
│   └── models/              # Database models
├── android/                 # Tasker & MacroDroid configs
├── scripts/                 # Setup automation
├── docs/                    # Documentation
├── main.py                  # Demo app entry point
└── requirements.txt
```

---

## 🔒 Security

- API key authentication
- Input validation (Pydantic)
- Rate limiting (configurable)
- HTTPS ready (nginx/caddy)
- IP whitelist support

See [docs/SECURITY.md](docs/SECURITY.md)

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
lsof -i :8080
# Kill process or change port
```

### Ollama Not Running
```bash
ollama serve
# Or use OpenAI: export LLM_PROVIDER=openai
```

### Database Error
```bash
rm -f ultron.db
python -c "from src.models.models import Base, engine; Base.metadata.create_all(engine)"
```

---

## 📖 Full Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Security Guide](docs/SECURITY.md)
- [Security Setup](docs/SECURITY_SETUP.md)

---

## 🤝 Contributing

1. Fork the repo
2. Create branch (`git checkout -b feature/amazing`)
3. Commit changes
4. Push and open PR

---

## 📧 Support

- **GitHub Issues**: https://github.com/gadelz/ultron-multi-device/issues
- **Demo**: https://ultron-demo.gadelz.repl.co

---

**Built with ❤️ by gadelz**
