# 🚀 OpenRun v1.0

> Run any Python AI model as an OpenAI-compatible API — instantly.

---

## 💡 What is OpenRun?

**OpenRun** lets you take *any Python AI model code* and expose it as a fully functional **OpenAI-compatible API** with **one line of code**.

No UI. No frontend. No setup headaches.

Just your model → API.

---

## ⚡ Features

* 🧠 Works with **any Python model code**
* 🔌 OpenAI-compatible API (`/v1/chat/completions`)
* 🔄 Full **messages support** (chat history, roles)
* ⚡ **Streaming support** (`stream=True`)
* 🌍 Public URL via tunnel (`--public`)
* 🔐 Auto API key generation
* 🧪 Works in **Google Colab, Jupyter, local**
* 🧩 Supports HuggingFace + custom models

---

## 🚀 Quick Start (1 Cell)

```python
from openrun import serve

def chat(messages):
    return "Hello from OpenRun!"

serve(fn=chat, public=True)
```

---

## 🌍 Output

```text
🚀 OpenRun running
🔐 API Key: sk-or-xxxx

🌍 Public URL: https://xxxx.trycloudflare.com
📡 Endpoint: /v1/chat/completions
```

---

## 🔌 Use with OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-url/v1",
    api_key="sk-or-xxxx"
)

response = client.chat.completions.create(
    model="openrun",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)
```

---

## ⚡ Streaming Example

```python
response = client.chat.completions.create(
    model="openrun",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="")
```

---

## 🧠 Using Your Own Model

Works with ANY code:

```python
def chat(messages):
    # your model logic
    return "Custom response"
```

OR

```python
def generate(prompt):
    return "Simple model"
```

OpenRun auto-detects and adapts.

---

## 🖥 CLI Usage

```bash
openrun serve my_model.py --public
```

---

## 🔐 API Key

* Auto-generated if not provided
* Or set manually:

```bash
openrun serve my_model.py --api-key mykey
```

---

## 📡 API Format

### Endpoint:

```
POST /v1/chat/completions
```

### Request:

```json
{
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "stream": false
}
```

---

## 🧠 How It Works

1. Loads your Python function
2. Wraps it as an API
3. Adds OpenAI compatibility
4. Optionally exposes it publicly

---

## 🎯 Use Cases

* Run LLMs in Colab as APIs
* Share models instantly
* Build custom AI backends
* Replace OpenAI API locally

---

## 🔥 Why OpenRun?

Because running models should be this simple:

```python
serve(fn=chat)
```

---

## 🚀 Installation

```bash
pip install openrun
```

---

## 🛠 Development

```bash
git clone https://github.com/<your-username>/openrun.git
cd openrun
pip install -e .
```

---

## 📦 Version

**v1.0 — Initial Release**

---

## 🤝 Contributing

PRs welcome! Feel free to improve adapters, streaming, or integrations.

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

---

## 🚀 Future Plans

* Real token streaming (HF streamer)
* Multi-model support
* Dashboard UI
* Cloud deployment

---

## ⚡ One Line Summary

> Turn any Python AI model into a public OpenAI API instantly.
