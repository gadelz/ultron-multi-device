ULTron Multi-Device Automation Architecture

## 1. System Architecture and Component Mapping

```
[User Voice/Text Command]
         |
         v
+------------------+
|   AI Core        |  <- Whisper (speech-to-text) + LLM (command parsing)
| (Termux/Server)  |
+--------+---------+
         | parsed Intent + Targets
         v
+------------------+
|   Gateway API    |  <- FastAPI server, webhook receiver
|   (localhost     |     + dispatcher + device registry
|    :8080)        |
+--------+---------+
         | HTTP POST /device/{id}/trigger
         v
+------------------+     +---------------------+     +-------------------+
|  Target Device 1 |     |  Target Device 2    |     |  Target Device 3  |
|  (Main Phone,    |     |  (Secondary Phone 1)|     |  (Secondary Phone 2)
|   e.g. Samsung)  |     |  e.g. Pixel)        |     |  e.g. Redmi)        |
|  Tasker Profile  |     |  MacroDroid Macro   |     |  MacroDroid Macro  |
+------------------+     +---------------------+     +-------------------+
         |                       |                         |
         v                       v                         v
   Wake + Unlock         Wake + Unlock            Wake + Unlock
   Answer/Open App       Launch YouTube           Launch YouTube
```

### Components Description

1. **AI Core** (Termux Laptop / NVIDIA Box)
   - `whisper.cpp` for offline speech-to-text
   - Local LLM (Mistral 7B / Llama 3) OR OpenAI API for intent extraction
   - Output: structured Intent JSON

2. **Gateway API** (FastAPI, port 8080)
   - Endpoints: `/webhook`, `/device/{id}/trigger`, `/broadcast`
   - Device registry (device_id, label, ip, port, auth_token, flavor=tasker/macrodroid)
   - Authentication (API key / HMAC)

3. **Termux/Server Worker**
   - Python worker that persists commands, retries failures, logs execution
   - Can be triggered by AI Core directly or gateway

4. **Target Devices**
   - Each device runs an HTTP listener (Tasker HTTP Get / MacroDroid Web Trigger) OR listens via FCM/MQTT
   - Action: Wake screen (turnScreenOn), unlock (keyguard dismiss), launch app (am start / Intent)

5. **Local Network Transport**
   - Primary: HTTP POST to each device's local IP:port
   - Fallback: MQTT broker (Mosquitto) on local network
   - FCM (push notifications) for devices outside LAN
