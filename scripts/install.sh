#!/bin/bash
# Quick install script for ULTron

set -e

echo "🚀 Installing ULTron Multi-Device Automation..."

# Check Python
python3 --version || { echo "❌ Python 3 required"; exit 1; }

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt

# Check Ollama
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found"
    if ! ollama list &> /dev/null; then
        echo "📥 Pulling LLM model (this may take a while)..."
        ollama pull llama3.2:latest
    fi
else
    echo "⚠️  Ollama not installed"
    echo "   Install: curl -fsSL https://ollama.com/install.sh | sh"
    echo "   Or set OPENAI_API_KEY for OpenAI provider"
fi

# Copy env file
cp .env.example .env 2>/dev/null || true

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env with your settings"
echo "   2. Start gateway: python -m src.gateway.server"
echo "   3. Register devices: see README.md"
echo "   4. Test: python scripts/test_llm_parser.py"
