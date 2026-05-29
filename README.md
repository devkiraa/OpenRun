# 🚀 OpenRun

> Expose any local AI model or Python function as a secure, public OpenAI-compatible API — in a single line of code.

OpenRun is a lightweight, developer-first runtime built using FastAPI, Uvicorn, and Cloudflared. It allows you to transform any model (from HuggingFace, AirLLM, Ollama, or simple custom Python functions) into a fully compatible OpenAI chat completion endpoint.

No UI bloat. No complex configuration files. Just your model → secure REST API.

---

## ✨ Key Features

* **🔌 OpenAI-Compatible API:** Native support for `/v1/chat/completions` supporting both standard JSON and real-time Server-Sent Event (SSE) streaming (`stream=True`).
* **🔐 Interactive Swagger UI (`/docs`):** Interactive browser testing sandbox with built-in HTTP Bearer padlock authorization (`bearerAuth`).
* **🧠 Master System Analyzer (`openrun master`):** Scans system hardware (CPU cores, RAM, GPU, VRAM) to recommend ideal model sizes and estimate inference speeds (Tokens/sec).
* **⚙️ Visual Settings Configurator (`openrun settings`):** Arrow-key visual dashboard in TTY terminals to adjust Cache paths, Ports, API Keys, and HF Tokens persistently.
* **🛡️ High-Grade Security:** Automatically enforces strict user-only file permissions (`0o700` directories and `0o600` configs) to guard sensitive API keys and Hugging Face tokens.
* **🌍 Instant Public URL (`--public`):** Boots a secure Cloudflare tunnel to safely bypass firewalls and expose local runtimes to the web with HTTPS.
* **📈 In-Place System Stats Logger:** Console HTTP request logs show real-time RAM and VRAM footprint consumption on every single successful endpoint hit.

---

## 🚀 Installation

Install the package in editable development mode:
```bash
git clone https://github.com/devkiraa/OpenRun.git
cd OpenRun
pip install -e .
```

---

## ⚡ Quick Start (In a Python Script or Jupyter Cell)

Expose any basic Python function as an OpenAI-compatible API:

```python
from openrun import serve

# 1. Define your custom logic
def chat(messages):
    user_prompt = messages[-1]["content"] if messages else ""
    return f"Processed query: {user_prompt}"

# 2. Expose it instantly
serve(fn=chat, port=8000, public=False)
```

**Output:**
```text
🚀 OpenRun running
🔐 API Key: sk-or-8c9df102...
🌍 URL: http://localhost:8000
📡 Endpoint: /v1/chat/completions
[INFO] GET / - Status: 200 (1.10ms) | RAM: 5.40/15.70 GB | VRAM: 0.85/4.00 GB
```

---

## 🖥 CLI Usage

OpenRun is designed around a visual CLI-first developer experience.

### 1. Launch a HuggingFace Model
```bash
openrun serve --model smollm2-135m
```

### 2. Launch a Custom Python File Model
Expose a `.py` model file:
```bash
openrun serve my_model.py --port 8080 --public
```
*Your python file must expose a `generate(prompt: str) -> str` or `chat(messages: list) -> str` function.*

### 3. Analyze Local Hardware (`openrun master`)
Assess your host computer and receive tailored model loading suggestions:
```bash
openrun master
```
Estimates VRAM footprints, suggests 4-bit/8-bit quantization flags, and predicts expected tokens per second.

### 4. Adjust Configurations (`openrun settings`)
Launch the interactive configurator menu to persistent adjust keys and tokens:
```bash
openrun settings
```
*In non-interactive environments (pipes or CI pipelines), this command safely prints a plain diagnostic list of currently configured parameters.*

---

## 🧪 Interactive API Documentation

All frontend routes are converted into a pure API provider. Visiting `http://localhost:8000/chat` automatically redirects you to the interactive Swagger UI:

1. Open **`http://localhost:8000/docs`** in your browser.
2. Click the **"Authorize"** padlock button in the top-right.
3. Type your configured or auto-generated Bearer API Key and authorize.
4. Try out the `/v1/chat/completions` endpoint directly inside the browser.

---

## 🔌 API Consumer Integration Examples

### 1. Python (Official `openai` SDK)
```python
from openai import OpenAI

# Connect to the local or public OpenRun server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="your_configured_api_key"
)

# Streaming execution
stream = client.chat.completions.create(
    model="openrun",
    messages=[{"role": "user", "content": "Tell me a short story."}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 2. Raw HTTP Requests (cURL)
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_configured_api_key" \
  -d '{
    "model": "openrun",
    "messages": [{"role": "user", "content": "Explain gravity in a single sentence."}],
    "stream": false
  }'
```

---

## 🤝 Contributing

Contributions are welcome! Please ensure all code adheres to:
1. Modular architecture layout rules.
2. OpenAI compatibility compliance.
3. Clean, zero-dependency console graphics.

Give it a ⭐ on GitHub if you enjoy building with OpenRun!
