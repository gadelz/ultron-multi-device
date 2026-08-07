# Dev.to / Medium Article Templates

---

## Article 1: How I Built a Multi-Device Automation System with FastAPI

**Slug:** how-i-built-a-multi-device-automation-system-with-fastapi
**Cover Image:** [Architecture diagram]
**Reading Time:** 8 min

### Introduction
I was tired of manually controlling my 3 Android phones. Each morning, I had to wake them up, unlock them, and open YouTube to play my podcast. So I built ULTron.

In this article, I'll show you how to build a voice-controlled multi-device automation system using FastAPI, Ollama, and Android automation tools.

### The Architecture
[Include diagram]

**Components:**
1. **AI Core** - Parses voice commands using Ollama (local LLM)
2. **Gateway API** - FastAPI server that orchestrates device commands
3. **Android Clients** - Tasker/MacroDroid apps on each phone
4. **Database** - SQLite for device registry

### Setting Up the Gateway

```python
# gateway/server.py
from fastapi import FastAPI, HTTPException, Depends
import httpx, asyncio

app = FastAPI(title="ULTron Gateway")

@app.post("/webhook")
async def dispatch_command(cmd: Command):
    jobs = [_schedule_target(device) for device in cmd.targets]
    results = await asyncio.gather(*jobs)
    return {"results": results}
```

### Android Setup

[Tasker configuration screenshot]
[MacroDroid configuration screenshot]

### The Staggered Execution Problem

When multiple devices respond simultaneously, network conflicts occur. Solution: stagger the execution with delays.

```python
# Schedule with delays
for idx, target in enumerate(cmd.targets):
    delay = idx * 800  # 800ms between devices
    jobs.append(_schedule_target(db, cmd, target, delay))
```

### Results

- Voice command → All devices respond in < 3 seconds
- Zero network conflicts
- Fully offline (local LLM)

### Next Steps

1. Deploy to Render (free tier)
2. Add HTTPS with nginx
3. Configure Android devices

**GitHub Repository:** https://github.com/gadelz/ultron-multi-device

---

## Article 2: Voice Command Parsing with Ollama (Local LLM)

**Slug:** voice-command-parsing-with-ollama-local-llm
**Cover Image:** [LLM integration diagram]
**Reading Time:** 6 min

### Why Local LLM?

Cloud APIs cost money and require internet. For a device automation system, local is better:
- Free (no API costs)
- Private (no data leaves your network)
- Fast (no network latency)

### Implementation

```python
# llm/core.py
import ollama

class OllamaProvider(BaseLLMProvider):
    async def parse_intent(self, transcript: str) -> dict:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[{"role": "user", "content": transcript}]
        )
        return parse_json(response['message']['content'])
```

### Fallback Parser

When Ollama isn't available, use keyword-based parsing:

```python
def fallback_parse(transcript: str) -> dict:
    t = transcript.lower()
    if any(k in t for k in ["wake", "unlock"]):
        return {"intent": "wake_all"}
    elif any(k in t for k in ["youtube", "play"]):
        return {"intent": "play_youtube_all"}
    # ... etc
```

### Performance

- Ollama: ~200ms inference time
- Fallback: < 1ms
- Total pipeline: < 500ms end-to-end

### Getting Started

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.2:latest

# Run server
ollama serve
```

**Full code:** https://github.com/gadelz/ultron-multi-device

---

## Article 3: Deploying Python APIs for Free (Render vs Fly.io vs Replit)

**Slug:** deploying-python-apis-for-free-render-vs-fly-io-vs-replit
**Cover Image:** [Platform comparison graphic]
**Reading Time:** 7 min

### The Problem

You built an awesome Python API. Now how do you deploy it without spending money?

### Option 1: Render (Easiest)

**Pros:**
- One-click GitHub deploy
- Free HTTPS
- Auto-scaling

**Cons:**
- 15-minute sleep after inactivity
- 512MB RAM limit

**Setup:**
```bash
# render.yaml
services:
  - type: web
    name: ultron-gateway
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
```

### Option 2: Fly.io (Best Performance)

**Pros:**
- Real VM (not container)
- No sleep mode
- Global edge locations

**Cons:**
- More complex setup
- Limited free tier (3 VMs)

**Setup:**
```bash
fly launch --name ultron-gateway
fly deploy
```

### Option 3: Replit (Fastest to Start)

**Pros:**
- Instant deployment
- No config needed
- Great for prototyping

**Cons:**
- Limited resources
- Not production-ready

**Setup:**
```bash
# Just import from GitHub and click Run
```

### My Recommendation

| Use Case | Platform |
|----------|----------|
| Testing/Prototyping | Replit |
| Production (small) | Render |
| Production (medium) | Fly.io |

**Full deployment guide:** https://github.com/gadelz/ultron-multi-device/blob/main/DEPLOY.md

---

## Article 4: Tasker + MacroDroid: The Android Automation Power Couple

**Slug:** tasker-macrodroid-android-automation
**Cover Image:** [Android setup screenshot]
**Reading Time:** 5 min

### Why Two Apps?

- **Tasker**: More powerful, steeper learning curve
- **MacroDroid**: Easier to use, good for simple automations

### Tasker HTTP Server Setup

1. Create new profile → Network → HTTP Server
2. Set port: 1820
3. Set path: /tasker/trigger
4. Add authentication header

### MacroDroid Web Trigger Setup

1. Create new macro
2. Trigger → HTTP Server
3. Configure POST endpoint
4. Add actions

### Action Sequence

```
1. Screen On
2. Dismiss Keyguard  
3. Launch App (YouTube)
```

### Security Considerations

- Use unique tokens per device
- Enable HTTPS
- Restrict to local network

**Full configuration:** https://github.com/gadelz/ultron-multi-device/tree/main/android

---

## SEO Tips

1. **Title:** Include keyword + benefit
2. **URL:** Short, descriptive slug
3. **Meta Description:** 150-160 chars with CTA
4. **Tags:** 4-5 relevant tags
5. **Images:** Alt text with keywords
6. **Internal Links:** Link to related articles
7. **External Links:** Link to GitHub, docs

---

## Publishing Checklist

- [ ] Write compelling title
- [ ] Add cover image (1200x630)
- [ ] Write meta description
- [ ] Add 4-5 tags
- [ ] Include code snippets
- [ ] Add screenshots where helpful
- [ ] Link to GitHub repo
- [ ] Add CTA (star, contribute, etc.)
- [ ] Share on Twitter/LinkedIn after publish
