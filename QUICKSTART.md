# ULTron Multi-Device Automation - Quick Reference

## 🚀 Start Gateway
```bash
# Set environment
export ULTRON_API_KEY=your-secret-key
export LLM_PROVIDER=ollama  # or openai

# Run
python -m uvicorn src.gateway.server:app --port 8080
```

## 📱 Test Parser
```bash
python scripts/test_llm_parser.py
```

## 🔒 Security Setup (Production)
```bash
# Development (self-signed)
sudo bash scripts/setup-security.sh

# Production (Let's Encrypt)
sudo bash scripts/setup-letsencrypt.sh your-domain.com
```

## 📖 Full Docs
- README.md - Getting started
- docs/SECURITY.md - Security guide
- docs/SECURITY_SETUP.md - HTTPS + Firewall setup

## 🔗 GitHub
https://github.com/gadelz/ultron-multi-device
