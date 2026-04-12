# 🤖 AGENTS.md — OpenRun AI Build Guide

This file defines how AI agents should understand, build, and extend the OpenRun project.

---

## 🧠 Project Overview

**OpenRun** is a developer tool that:

> Converts any local AI model into an OpenAI-compatible API with a public URL.

It enables developers to:

* Run models locally (Colab, GPU, PC)
* Expose them instantly as APIs
* Use them with OpenAI-compatible SDKs

---

## 🎯 Core Responsibilities of AI Agent

When working on this repository, you must:

1. Read `README.md` fully before making changes
2. Maintain modular architecture
3. Ensure OpenAI API compatibility
4. Keep developer experience simple (CLI-first)
5. Avoid breaking existing interfaces

---

## 🧱 Architecture Rules

The project MUST follow this modular structure:

```id="j2t3qa"
openrun/
├── cli/          # CLI commands
├── api/          # FastAPI routes
├── model/        # Model loading & inference
├── adapters/     # Model adapters (HF, custom)
├── core/         # Config, logging, state
├── network/      # Server + Cloudflare tunnel
├── security/     # API keys, rate limiting
├── streaming/    # SSE support
├── utils/        # Helpers
```

---

## ⚙️ Coding Principles

* Write clean, readable Python code
* Prefer simplicity over complexity
* Avoid tight coupling between modules
* Use clear function and class names
* Add comments where logic is non-obvious
* Do NOT introduce unnecessary dependencies

---

## 🔌 API Standards

The API must remain compatible with:

* OpenAI Chat Completions API

### Required Endpoint

```id="1gn9s9"
POST /v1/chat/completions
```

### Requirements:

* Accept `messages` array
* Support roles: `user`, `assistant`, `system`
* Return response in OpenAI format (`choices`, `message`, etc.)
* Support future streaming (SSE)

---

## 🧩 Model System Rules

The system must support:

### 1. HuggingFace Models

Loaded via CLI:

```bash
openrun serve --model <model_name>
```

### 2. Custom Python Models

Loaded via file:

```bash
openrun serve my_model.py
```

Custom file must expose:

```python
def generate(prompt: str) -> str:
    ...
```

---

## 🔁 Adapter Pattern (CRITICAL)

All models MUST be accessed via adapters.

### Base Adapter Interface:

```python
class BaseAdapter:
    def load(self): pass
    def generate(self, prompt: str) -> str: pass
```

Do NOT call models directly outside adapters.

---

## ☁️ Cloudflare Integration Rules

When `--public` flag is used:

* Start a Cloudflare tunnel
* Expose local server
* Print public URL clearly
* Ensure API works via that URL

Use subprocess or CLI invocation.

---

## 🔐 Security Rules

* API key support must be optional
* If enabled:

  * Require `Authorization: Bearer <key>`
* Do NOT hardcode keys unless default fallback

---

## ⚡ CLI Behavior

Main command:

```bash
openrun serve
```

### Supported Flags:

* `--model <name>`
* `--file <path>`
* `--port <port>`
* `--public`
* `--api-key <key>`

CLI must:

* Load model
* Start server
* Optionally start tunnel

---

## 🌐 Server Rules

* Use FastAPI
* Use uvicorn
* Must support async endpoints where needed
* Keep server initialization separate from CLI

---

## 📡 Streaming (Planned / Partial)

* Use Server-Sent Events (SSE)
* Follow OpenAI streaming format
* Can be implemented later if not complete

---

## 📦 Packaging Rules

* Use `pyproject.toml`
* Expose CLI via:

```toml
[project.scripts]
openrun = "openrun.cli.main:main"
```

* Ensure package is installable via:

```bash
pip install -e .
```

---

## 🧪 Testing Expectations

* Code should run without errors
* Imports must resolve correctly
* CLI should start successfully
* API endpoint should return valid responses

---

## 🚫 Things to Avoid

* Do NOT mix business logic with API routes
* Do NOT tightly couple model loading with API layer
* Do NOT break OpenAI API format
* Do NOT assume GPU availability
* Do NOT add unnecessary UI components

---

## 🚀 Development Workflow for AI Agent

When implementing features:

1. Plan structure first
2. Create/update relevant module
3. Ensure imports are correct
4. Test flow:
   CLI → API → Model → Response
5. Keep changes minimal and scoped

---

## 🧠 Future Extensions (Keep in Mind)

Design should allow:

* Multi-model support
* Request queue system
* Rate limiting
* Usage tracking
* Distributed workers
* Dashboard UI

---

## 💡 Philosophy

OpenRun is:

* Minimal but powerful
* Developer-first
* Infrastructure, not UI

---

## ✅ Definition of Done

A feature is complete when:

* It works via CLI
* It integrates cleanly into architecture
* It does not break existing functionality
* It follows OpenAI-compatible API format

---

## 🔥 Final Note

You are not just writing code.

You are building a **framework for exposing AI models as APIs**.

Think in systems, not scripts.
