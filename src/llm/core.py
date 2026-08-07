from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import os
import json
from dataclasses import dataclass

@dataclass
class LLMConfig:
    provider: str = "ollama"
    model: str = "llama3.2:latest"
    host: str = "http://localhost:11434"
    api_key: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 1024
    system_prompt: str = ""

class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        pass

    @abstractmethod
    async def parse_intent(self, transcript: str, system_prompt: str = "") -> dict:
        pass

class OllamaProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None

    async def chat(self, messages: list[dict]) -> str:
        try:
            import ollama
            response = ollama.chat(
                model=self.config.model,
                messages=messages,
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                }
            )
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama chat failed: {e}")

    async def parse_intent(self, transcript: str, system_prompt: str = "") -> dict:
        prompt = system_prompt or self.config.system_prompt
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Parse this command: {transcript}"}
        ]
        response = await self.chat(messages)
        # Try to extract JSON
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                json_str = response[start:end+1]
                return json.loads(json_str)
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse LLM response", "raw": response}

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None

    async def chat(self, messages: list[dict]) -> str:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(base_url=self.config.host, api_key=self.config.api_key)
        response = await client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return response.choices[0].message.content

    async def parse_intent(self, transcript: str, system_prompt: str = "") -> dict:
        prompt = system_prompt or self.config.system_prompt
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Parse this command: {transcript}"}
        ]
        response = await self.chat(messages)
        try:
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                return json.loads(response[start:end+1])
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse", "raw": response}

class LLMClient:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.provider = self._create_provider()
        self._system_prompt = self.config.system_prompt or self._default_system_prompt()

    def _create_provider(self) -> BaseLLMProvider:
        if self.config.provider == "ollama":
            return OllamaProvider(self.config)
        elif self.config.provider == "openai":
            return OpenAIProvider(self.config)
        else:
            raise ValueError(f"Unknown provider: {self.config.provider}")

    def _default_system_prompt(self) -> str:
        return """You are a multi-device voice command router for the ULTron system.
Your job is to parse user commands into structured JSON for device orchestration.

Valid intents:
- wake_all: Wake and unlock all devices
- play_youtube_all: Play YouTube on all devices
- answer_call: Answer an incoming call on specific device
- custom: Custom action with specific device targets

JSON schema:
{
  "intent": "wake_all|play_youtube_all|answer_call|custom",
  "correlate_id": "unique-request-id",
  "targets": [
    {
      "device_id": "string",
      "action": "wake_unlock|play_media|answer_call",
      "delay_ms": 0,
      "payload": {}
    }
  ]
}

Rules:
1. Only output valid JSON, no commentary
2. Use device IDs from the registered list if provided
3. Set appropriate delays for staggered execution
4. For "play_youtube_all", include YouTube query/deep_link in payload

If the command is unclear, set intent to "custom" with deny_reason."""

    async def parse_command(self, transcript: str) -> dict:
        return await self.provider.parse_intent(transcript, self._system_prompt)
