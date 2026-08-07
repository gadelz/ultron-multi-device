from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from enum import Enum

class DeviceFlavor(str, Enum):
    tasker = "tasker"
    macrodroid = "macrodroid"

class DeviceAction(str, Enum):
    wake_unlock = "wake_unlock"
    launch_app = "launch_app"
    play_media = "play_media"
    answer_call = "answer_call"
    custom_sh = "custom_sh"
    custom_am = "custom_am"

class DeviceTarget(BaseModel):
    device_id: str = Field(..., description="Unique device ID registered in system")
    action: DeviceAction
    payload: dict = Field(default_factory=dict, description="Action parameters")
    delay_ms: int = Field(default=0, ge=0, description="Delay before execution (ms)")

class Command(BaseModel):
    intent: Literal["wake_all", "play_youtube_all", "answer_call", "custom"]
    targets: List[DeviceTarget]
    correlate_id: Optional[str] = Field(default=None, description="Request correlation ID")
    created_by: Optional[str] = "ai-core"

class IntentParseRequest(BaseModel):
    transcript: str = Field(..., description="Raw text / whisper transcript")
    speaker_id: Optional[str] = None
