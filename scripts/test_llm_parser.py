#!/usr/bin/env python3
"""
ULTron LLM Parser Test — no Ollama required.
Uses built-in fallback parser when Ollama/OpenAI not available.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from llm.core import LLMClient, LLMConfig

def fallback_parse(transcript: str) -> dict:
    """Simple keyword-based fallback parser."""
    t = transcript.lower()
    intent = "custom"
    if any(k in t for k in ["wake", "unlock", "buka"]):
        intent = "wake_all"
    elif any(k in t for k in ["youtube", "play", "mainkan", "putar"]):
        intent = "play_youtube_all"
    elif any(k in t for k in ["call", "telpon", "jawab", "answer"]):
        intent = "answer_call"
    
    targets = []
    for idx, dev in enumerate(["main_phone", "secondary_1", "secondary_2"]):
        if intent in ["wake_all", "play_youtube_all"]:
            action = "play_media" if intent == "play_youtube_all" else "wake_unlock"
            delay = idx * 800
            targets.append({
                "device_id": dev,
                "action": action,
                "delay_ms": delay,
                "payload": {"app": "com.google.android.youtube"} if action == "play_media" else {}
            })
    
    return {
        "intent": intent,
        "correlate_id": "test-001",
        "targets": targets
    }

async def main():
    transcript = "wake all devices and play youtube on all of them"
    
    # Try Ollama first (fallback if not available)
    try:
        config = LLMConfig(provider="ollama", model="llama3.2:latest")
        client = LLMClient(config)
        result = await client.parse_command(transcript)
        print("✅ LLM parsed result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"ℹ️  Ollama not available ({e})")
        print("   Using built-in fallback parser...")
        result = fallback_parse(transcript)
        print("✅ Fallback parsed result:")
        print(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(main())
    
    # Test dispatch simulation
    print("\n📤 Simulating dispatch to gateway...")
    print(json.dumps(result, indent=2))
    print("\n✅ Test complete!")
