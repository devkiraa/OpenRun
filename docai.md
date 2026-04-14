# 🧠 OpenRun — AI-Oriented Documentation (docai.md)

> This document is designed for **AI agents and developers using AI tools** to understand, extend, and integrate OpenRun.

---

# 🚀 What is OpenRun?

**OpenRun** is a lightweight runtime that allows any Python function or model to be exposed as an **OpenAI-compatible API** with minimal code.

---

## 🔑 Core Idea

Turn this:

```python
def chat(messages):
    return "Hello"
```

Into this:

```text
POST /v1/chat/completions
```

Accessible via:

* HTTP
* Public URL (Cloudflare)
* OpenAI-compatible clients

---

# ⚙️ How OpenRun Works (Architecture)

---

## 🧩 1. Entry Point

### Python usage:

```python
from openrun import serve

serve(fn=chat, public=True)
```

---

### CLI usage:

```bash
openrun serve my_model.py --public
```

---

## 🧠 2. Adapter Layer

OpenRun converts user code into a standard interface using adapters.

### Types:

* `InlineAdapter` → wraps Python function
* `CustomAdapter` → loads `.py` files
* `HuggingFaceAdapter` → runs transformer models

---

### Standard Interface:

```python
generate(input_data: list) -> str
stream(input_data: list) -> generator
```

---

## 🌐 3. API Layer

Built using FastAPI.

### Endpoints:
```text
POST /v1/chat/completions  # Main OpenAI-compatible API
GET  /                     # Root discovery and info
GET  /health               # Health check ("status": "ok", "service": "OpenRun API")
```

### Logging & Errors:
If an error occurs (e.g., `404 Not Found`, `401 Unauthorized`), the OpenRun API server logs it clearly in the console with color-coded warnings, ensuring missing routes or invalid API Keys are easily debugged while keeping success (200) traffic completely silent.

---

### Request format:

```json
{
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "stream": false
}
```

---

### Response format:

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hello!"
      }
    }
  ]
}
```

---

## ⚡ 4. Streaming System

If:

```json
"stream": true
```

OpenRun returns **Server-Sent Events (SSE)**:

```text
data: {"choices":[{"delta":{"content":"Hel"}}]}

data: {"choices":[{"delta":{"content":"lo"}}]}

data: [DONE]
```

---

## 🧠 5. Model Execution Flow

```
Request → API Route → Adapter → Model → Response → Client
```

---

## 🔐 6. Authentication

Uses API key:

```text
Authorization: Bearer sk-or-xxxx
```

---

## 🌍 7. Public Access & UI (Cloudflare)

If enabled:

```python
serve(fn=chat, public=True)
```

OpenRun:

1. Starts local server quietly.
2. Starts Cloudflare tunnel (`subprocess` with verbose logs totally silenced via `DEVNULL`).
3. Extracts public URL and draws a clean ASCII art box around the public endpoint and the requested `API_KEY` to guarantee a perfect Developer Experience (DX).
4. Any missing Auth returns `401 Unauthorized`. Any missing route returns `404 Not Found` directly into the cleanly formatted console logs!

---

# 🔄 Internal Flow

---

## 🧠 Serve Function Flow

```
1. Configure runtime
2. Wrap user function in adapter
3. Start FastAPI server (thread)
4. Wait until server is ready
5. Start Cloudflare tunnel (optional)
6. Keep process alive
```

---

## ⚡ Streaming Flow

```
Request (stream=true)
→ Adapter.stream()
→ Generator yields tokens
→ SSE response
```

---

# 📦 Key Components

---

## 📁 server.py

* Entry point for runtime
* Starts server + tunnel

---

## 📁 adapters/

* Handles model abstraction

### Files:

* `base.py`
* `custom.py`
* `huggingface.py`

---

## 📁 api/

* Routes + schemas
* Handles requests

---

## 📁 network/

* FastAPI app
* Cloudflare tunnel logic

---

## 📁 core/

* Global state
* Config handling

---

# 🧠 Design Principles

---

## 1. Minimal Input

User provides only:

```python
def chat(messages): ...
```

---

## 2. Standard Output

Always OpenAI-compatible:

```json
/v1/chat/completions
```

---

## 3. Plug-and-Play

Supports:

* local models
* HuggingFace models
* custom logic

---

## 4. No Frontend Required

API-first design

---

# 🔌 Extending OpenRun

---

## Add New Adapter

Implement:

```python
class MyAdapter(BaseAdapter):
    def load(self): ...
    def generate(self, input_data): ...
    def stream(self, input_data): ...
```

---

## Modify API Behavior

Edit:

```text
api/routes.py
```

---

## Add Middleware / Auth

Edit:

```text
api/dependencies.py
```

---

# 🧪 Testing

---

## Local test:

```python
serve(fn=chat)
```

---

## Curl test:

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
-H "Authorization: Bearer sk-or-xxxx" \
-H "Content-Type: application/json" \
-d '{"messages":[{"role":"user","content":"Hello"}]}'
```

---

# ⚠️ Limitations

---

* Single-model runtime (currently)
* No persistence layer
* No built-in UI
* Depends on local compute

---

# 🚀 Future Directions

---

* Playground UI
* Multi-model routing
* Plugin system
* Deployment integrations
* Dashboard

---

# 💡 Summary

---

OpenRun provides:

* 🧠 Model abstraction
* 🌐 API standardization
* ⚡ Streaming support
* 🔐 Authentication
* 🌍 Public exposure

---

## 🔥 Core Value

> “Run any AI model as an OpenAI-compatible API in one line.”

---

# 🧠 For AI Agents

---

When working with OpenRun:

1. Use `/v1/chat/completions`
2. Always pass `messages`

---

# ❗ CRITICAL RULES (MUST FOLLOW)

OpenRun is a runtime platform.

---

## 🚫 NEVER DO THESE

When writing code using OpenRun, you MUST NOT:

* write FastAPI server manually
* use uvicorn directly
* manage sockets or ports
* install or run cloudflared manually
* use subprocess for tunnels
* create infinite loops for server
* implement API routes yourself

---

## ✅ ALWAYS DO THIS

Only write model logic:

```python
def chat(messages):
    return "response"
```

Then expose it using:

```python
from openrun import serve

serve(fn=chat)
```

---

## 🧠 RESPONSIBILITY SPLIT

| Component      | Responsible        |
| -------------- | ------------------ |
| Model logic    | User / AI          |
| API server     | OpenRun            |
| Streaming      | OpenRun            |
| Authentication | OpenRun            |
| Public URL     | OpenRun (optional) |

---

## 🎯 DESIGN PRINCIPLE

OpenRun abstracts ALL infrastructure.

AI should NEVER reimplement infrastructure.

---

## ❗ IMPORTANT

If AI generates:

* FastAPI app
* uvicorn.run()
* subprocess tunnels

👉 That is WRONG.

---

## ✅ CORRECT USAGE

Minimal example:

```python
from openrun import serve

def chat(messages):
    return "Hello"

serve(fn=chat)
```

---

## 🔥 SUMMARY

OpenRun = infrastructure layer
User code = model logic only
3. Use `stream=true` for streaming
4. Include API key
5. Expect OpenAI-like responses

---

## 📌 Important

* Do NOT assume model type
* Adapter handles execution
* Always use standard schema

---

# ✅ End of docai.md
