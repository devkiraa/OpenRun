# 🔌 OpenRun Developer & API Guide

OpenRun converts local Python AI models into an **OpenAI-compatible REST API** in a single line of code. It features standard endpoints, built-in rate-limiting and performance spec loggers, and a fully interactive documentation sandbox.

---

## 🔑 Setting & Configuring Your API Key

Authentication is managed via standard **HTTP Bearer Tokens** (`Authorization: Bearer <key>`). You have three flexible ways to specify the API key:

### 1. Interactive CLI Configuration Dashboard
You can visually configure a default, persistent API key for all future OpenRun servers:
```bash
openrun settings
```
* Use your arrow keys to select **`Default API Key`**.
* Type your key or clear it by typing `None`. 
* Settings are securely saved to your local config at `~/.openrun/settings.json`.

### 2. Command Line Flag
Provide a temporary API key directly at startup:
```bash
openrun serve --model smollm2-135m --api-key my_custom_secret_key
```

### 3. Automatic Random Fallback
If no key is configured in settings and no flag is passed, OpenRun automatically generates a secure token on boot and displays it clearly in your terminal console:
```text
🚀 OpenRun running
🔐 API Key: sk-or-a78b9c...
🌍 URL: http://localhost:8000
```

> [!NOTE]
> Setting the API key is completely optional. If you clear the key in `settings` and don't provide a flag or program argument, the API runs in **public mode**, allowing all requests without any authorization headers.

---

## 🧪 Interactive Testing with Swagger UI

OpenRun hosts an interactive API documentation interface directly on the server:

1. Start your model server (e.g. `openrun serve --model smollm2-135m`).
2. Navigate to **`http://localhost:8000/docs`** (or the Cloudflare public tunnel URL with `/docs` appended).
3. Click the **"Authorize"** button in the top-right corner of the page.
4. Input your configured API key in the value box and click **Authorize**.
5. Find the `/v1/chat/completions` endpoint, click **"Try it out"**, modify the payload, and hit **Execute** to view live streaming or standard responses.

---

## 📡 API Endpoints Reference

### 1. Chat Completions
* **Endpoint:** `POST /v1/chat/completions`
* **Headers:** 
  * `Content-Type: application/json`
  * `Authorization: Bearer <your-api-key>` (if enabled)

#### Request Body Schema
```json
{
  "model": "openrun",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Introduce yourself in one sentence."}
  ],
  "stream": false
}
```

---

## 💻 Consumer Integration Examples

### 1. Raw HTTP Requests (cURL)

#### Standard (Non-Streaming)
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my_custom_secret_key" \
  -d '{
    "model": "openrun",
    "messages": [
      {"role": "user", "content": "Explain gravity in one sentence."}
    ],
    "stream": false
  }'
```

#### Event-Stream (Streaming)
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my_custom_secret_key" \
  -d '{
    "model": "openrun",
    "messages": [
      {"role": "user", "content": "Write a short poem about coding."}
    ],
    "stream": true
  }'
```

---

### 2. Python (Official `openai` SDK)

To integrate seamlessly into existing AI agents and frameworks, use the standard OpenAI client:

```python
from openai import OpenAI

# Initialize the client pointing to your OpenRun server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="my_custom_secret_key"  # Use your configured key
)

# 1. Non-Streaming Request
print("--- Standard Response ---")
response = client.chat.completions.create(
    model="openrun",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    stream=False
)
print(response.choices[0].message.content)

# 2. Streaming Response
print("\n--- Streaming Response ---")
stream = client.chat.completions.create(
    model="openrun",
    messages=[
        {"role": "user", "content": "Write a 3-step guide to baking bread."}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

---

### 3. Python (Bare `requests` Library)

If you prefer lightweight HTTP calls without installing the OpenAI SDK:

```python
import requests
import json

url = "http://localhost:8000/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer my_custom_secret_key"
}

payload = {
    "model": "openrun",
    "messages": [{"role": "user", "content": "Hi there!"}],
    "stream": False
}

response = requests.post(url, headers=headers, json=payload)
print(response.json()["choices"][0]["message"]["content"])
```

---

### 4. JavaScript / Node.js (`fetch`)

For frontend interfaces or Node.js backend pipelines:

```javascript
const apiKey = "my_custom_secret_key";
const url = "http://localhost:8000/v1/chat/completions";

async function getCompletion() {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: "openrun",
      messages: [{ role: "user", content: "Hello!" }],
      stream: false
    })
  });

  const data = await response.json();
  console.log(data.choices[0].message.content);
}

getCompletion();
```
