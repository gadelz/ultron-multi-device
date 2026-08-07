#!/usr/bin/env python3
"""
ULTron Orkestrator — with LLM Integration
Uses LLMClient to parse user transcript into structured commands.
"""

import os, sys, json, asyncio, argparse, uuid
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from llm.core import LLMClient, LLMConfig

GATEWAY = os.getenv("ULTRON_GATEWAY", "http://localhost:8080")
API_KEY = os.getenv("ULTRON_API_KEY", "changeme-secret-key")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "openai"
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:latest")

REGISTERED_DEVICES = [
    {"device_id": "main_phone", "flavor": "tasker", "host": "192.168.1.50", "port": 1820, "path": "/tasker/trigger"},
    {"device_id": "secondary_1", "flavor": "macrodroid", "host": "192.168.1.51", "port": 1880, "path": "/macrodroid/trigger"},
    {"device_id": "secondary_2", "flavor": "macrodroid", "host": "192.168.1.52", "port": 1880, "path": "/macrodroid/trigger"},
]

async def amain(transcript: str):
    print(f"[*] Transcript: {transcript}")

    # Initialize LLM client
    config = LLMConfig(
        provider=LLM_PROVIDER,
        model=LLM_MODEL,
    )
    llm = LLMClient(config)

    # Parse intent with LLM
    print("[*] Sending to LLM for intent parsing...")
    cmd = await llm.parse_command(transcript)
    print(f"[*] LLM parsed command: {json.dumps(cmd, indent=2)}")

    if cmd.get("intent") == "custom" and cmd.get("deny_reason"):
        print(f"[!] Deny or no-op: {cmd.get('deny_reason')}")
        return cmd

    # Validate/fix targets if needed
    if "targets" not in cmd:
        cmd["targets"] = []
    if not cmd.get("correlate_id"):
        cmd["correlate_id"] = str(uuid.uuid4())

    res = await dispatch_to_gateway(cmd)
    print(f"[*] Gateway response: {json.dumps(res, indent=2)}")
    return res

async def dispatch_to_gateway(command: dict) -> dict:
    import httpx
    url = f"{GATEWAY}/webhook"
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
    async with httpx.AsyncClient(timeout=15.0) as c:
        r = await c.post(url, json=command, headers=headers)
        r.raise_for_status()
        return r.json()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("transcript", nargs="?", default=None)
    p.add_argument("--stdin", action="store_true")
    a = p.parse_args()

    if a.stdin:
        transcript = sys.stdin.read().strip()
    else:
        transcript = a.transcript or ""

    if not transcript:
        print("Usage: worker.py 'wake all and play youtube'  OR  worker.py --stdin")
        sys.exit(1)

    asyncio.run(amain(transcript))

if __name__ == "__main__":
    main()
