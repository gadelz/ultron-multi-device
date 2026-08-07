# ULTron Multi-Device Automation

> **AI-powered multi-device orchestration system** — control Android phones, tablets, and other devices via voice commands or API. Built with FastAPI, Ollama (local LLM), and Tasker/MacroDroid.

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

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Android devices with Tasker/MacroDroid
- Ollama (optional, for LLM-based parsing)

### Installation

```bash
# Clone repository
git clone https://github.com/gadelz/ultron-multi-device.git
cd ultron-multi-device

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings
```

### Start Gateway

```bash
# Direct
python -m uvicorn src.gateway.server:app --host 0.0.0.0 --port 8080

# Or with Docker
docker-compose up -d
```

### Register Devices

```bash
curl -X POST http://localhost:8080/device/register \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "main_phone",
    "flavor": "tasker",
    "host": "192.168.1.50",
    "port": 1820,
    "path": "/tasker/trigger",
    "auth_token": "your-device-token"
  }'
```

### Test the System

```bash
# Test with fallback parser (no Ollama required)
python scripts/test_llm_parser.py

# Test with LLM (requires Ollama running)
ollama pull llama3.2:latest
python scripts/test_llm_parser.py
```

## 📱 Android Setup

### Tasker (Primary Phone)

1. **Install Tasker** from Play Store
2. **Import Profile**: `android/tasker/tasker_project.xml`
3. **Configure HTTP Server**:
   - Port: `1820`
   - Path: `/tasker/trigger`
   - Auth Header: `Authorization: Bearer <your-token>`
4. **Create Tasks** for each action:
   - `wake_unlock` → Turn Screen On + Dismiss Keyguard
   - `play_media` → Launch YouTube with deep link
   - `answer_call` → Answer incoming call

### MacroDroid (Secondary Devices)

1. **Install MacroDroid** from Play Store
2. **Create New Macro**:
   - **Trigger**: HTTP Server → POST `/macrodroid/trigger` port `1880`
   - **Actions**:
     1. Screen On
     2. Dismiss Keyguard
     3. Launch App → `com.google.android.youtube`
3. **Configure Auth**: Same token as main phone

## 🧠 LLM Integration

### Supported Providers

| Provider | Local | API Key | Model |
|----------|-------|---------|-------|
| Ollama | ✅ | ❌ | llama3.2, mistral, etc. |
| OpenAI | ❌ | ✅ | gpt-4o, gpt-4o-mini |
| Compatible | ❌ | ✅ | vLLM, LocalAI, etc. |

### Configuration

```bash
# .env file
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2:latest

# OR for OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Fallback Parser

When no LLM is available, the system uses a built-in keyword parser:

```python
# Examples of fallback parsing:
"wake all devices"        → wake_all
"play youtube on all"     → play_youtube_all
"answer the call"         → answer_call
"unlock everything"       → wake_all
```

## 🔌 API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Gateway health check |
| POST | `/webhook` | Dispatch command to devices |
| POST | `/broadcast` | Fire action to all active devices |
| POST | `/device/register` | Register a target device |
| GET | `/devices` | List registered devices |

### Request/Response Examples

#### Register Device
```bash
POST /device/register
{
  "device_id": "main_phone",
  "label": "Samsung S24",
  "flavor": "tasker",
  "host": "192.168.1.50",
  "port": 1820,
  "path": "/tasker/trigger",
  "auth_token": "tok_main_phone"
}
```

#### Dispatch Command
```bash
POST /webhook
{
  "intent": "wake_all_play_youtube",
  "correlate_id": "req-001",
  "targets": [
    {
      "device_id": "main_phone",
      "action": "wake_unlock",
      "delay_ms": 0,
      "payload": {}
    },
    {
      "device_id": "main_phone",
      "action": "play_media",
      "delay_ms": 800,
      "payload": {
        "app": "com.google.android.youtube",
        "deep_link": "vnd.youtube://",
        "query": "https://youtube.com/watch?v=xyz"
      }
    }
  ]
}
```

#### Response
```json
{
  "correlate_id": "req-001",
  "results": [
    {
      "device_id": "main_phone",
      "status": "ok",
      "result": {"success": true}
    }
  ]
}
```

## 📁 Project Structure

```
ultron-multi-device/
├── src/
│   ├── gateway/
│   │   ├── server.py        # FastAPI gateway server
│   │   └── requirements.txt
│   ├── workers/
│   │   ├── worker.py        # AI core worker
│   │   └── workflow.*.yml   # Workflow definitions
│   ├── llm/
│   │   └── core.py          # LLM client (Ollama/OpenAI)
│   ├── schemas/
│   │   └── schemas.py       # Pydantic models
│   └── models/
│       └── models.py        # SQLAlchemy models
├── android/
│   ├── tasker/
│   │   └── tasker_project.xml
│   └── macrodroid/
│       └── macro.json
├── scripts/
│   ├── test_llm_parser.py   # Parser test script
│   └── install.sh           # Installation helper
├── docs/
│   ├── ARCHITECTURE.md      # Architecture documentation
│   └── components.json      # Component specs
├── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🐛 Troubleshooting

### Installation Issues

#### Python Dependencies Not Found
```bash
# Error: ModuleNotFoundError: No module named 'fastapi'
pip install -r requirements.txt

# If pip is outdated
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Ollama Not Running
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama service
ollama serve

# Pull model (if not present)
ollama pull llama3.2:latest
```

#### SQLite Database Error
```bash
# Clear and recreate database
rm -f ultron.db
python -c "from src.models.models import Base, engine; Base.metadata.create_all(engine)"
```

### Gateway Issues

#### Port Already in Use
```bash
# Check what's using port 8080
lsof -i :8080
# Or: netstat -tulpn | grep :8080

# Kill process or change port
export ULTRON_PORT=8081
uvicorn src.gateway.server:app --host 0.0.0.0 --port 8081
```

#### 403 Forbidden Error
```bash
# Check API key configuration
echo $ULTRON_API_KEY

# Verify header in curl request
curl -X POST http://localhost:8080/device/register \
  -H "X-API-Key: $ULTRON_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Android Connection Issues

#### Device Not Responding
```bash
# Check device connectivity
ping 192.168.1.50
telnet 192.168.1.50 1820

# Test HTTP directly
curl -X POST http://192.168.1.50:1820/tasker/trigger \
  -H "Authorization: Bearer tok_main_phone" \
  -H "Content-Type: application/json" \
  -d '{"action":"wake_unlock","payload":{}}'
```

#### Tasker/MacroDroid Not Triggering
1. **Check app permissions**: Ensure 'Display over other apps' is enabled
2. **Check battery optimization**: Whitelist Tasker/MacroDroid from battery saver
3. **Verify HTTP server is running**: Check Tasker's HTTP Server profile is active

### LLM Parser Issues

#### No Intent Parsed
```bash
# Test with explicit fallback
python scripts/test_llm_parser.py

# Check transcript format
echo "wake all devices" | python src/workers/worker.py --stdin
```

#### Ollama Timeout
```bash
# Increase timeout (default 30s)
export OLLAMA_TIMEOUT=60

# Use smaller model
export LLM_MODEL=phi3:latest  # Faster inference
```

## 🔒 Security

### API Keys
- Use strong random API keys for `ULTRON_API_KEY`
- Store in `.env` file, never commit to git
- Rotate keys periodically

### Network Security
- Run gateway behind reverse proxy (nginx/caddy) in production
- Use HTTPS for all API endpoints
- Restrict device IPs via firewall rules

### Android App Security
- Use unique tokens per device
- Enable HTTPS in Tasker/MacroDroid if possible
- Regularly audit device access

## 🚢 Docker Deployment

```bash
# Build and run with Docker
docker-compose up -d

# Check logs
docker-compose logs -f gateway

# Stop services
docker-compose down
```

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📧 Support

- **GitHub Issues**: https://github.com/gadelz/ultron-multi-device/issues
- **Documentation**: https://github.com/gadelz/ultron-multi-device/tree/main/docs

---

**Built with ❤️ by gadelz**
