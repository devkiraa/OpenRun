from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from openrun.api.schemas import ChatRequest
from openrun.core.state import get_global_state
from openrun.api.dependencies import verify_api_key
from openrun.model.inference import generate_response, stream_response
import time
import uuid
import os
import asyncio
import threading
from openrun.models.registry import PREDEFINED_MODELS

router = APIRouter()

# Concurrency limiter: max 1 inference at a time to prevent GPU OOM crashes
_inference_semaphore = asyncio.Semaphore(1)

# HTML template for the built-in web playground
@router.get("/chat")
async def chat_playground(request: Request):
    """
    Redirects to the interactive API documentation.
    """
    return RedirectResponse(url="/docs")


def _resolve_hf_token(optional_token: str | None = None) -> str | None:
    token = optional_token or os.getenv("HF_TOKEN")
    if token:
        return token

    try:
        from google.colab import userdata  # type: ignore
        token = userdata.get("HF_TOKEN")
    except Exception:
        token = None
    return token


def _set_loading_state(
    *,
    status: str,
    model_key: str | None = None,
    stage: str | None = None,
    message: str | None = None,
    progress: int | None = None,
    error: str | None = None,
):
    state = get_global_state()
    now = time.time()

    state.loading_status = status
    if model_key is not None:
        state.loading_model_key = model_key
    state.loading_stage = stage
    state.loading_message = message
    if progress is not None:
        state.loading_progress = max(0, min(100, int(progress)))
    state.loading_error = error

    if status in ("queued", "loading") and state.loading_started_at is None:
        state.loading_started_at = now
    if status in ("ready", "error", "idle"):
        if state.loading_started_at is None:
            state.loading_started_at = now
    state.loading_updated_at = now


def _loading_snapshot(state):
    elapsed = None
    if state.loading_started_at:
        elapsed = round(time.time() - state.loading_started_at, 1)

    return {
        "status": state.loading_status,
        "model_key": state.loading_model_key,
        "stage": state.loading_stage,
        "message": state.loading_message,
        "progress": state.loading_progress,
        "error": state.loading_error,
        "elapsed_seconds": elapsed,
        "updated_at": state.loading_updated_at,
    }


def _estimate_tokens(state, text: str) -> int:
    if not text:
        return 0
    if hasattr(state, "adapter") and state.adapter and hasattr(state.adapter, "tokenizer") and hasattr(state.adapter.tokenizer, "encode"):
        try:
            return len(state.adapter.tokenizer.encode(text))
        except Exception:
            pass
    return int(len(text.split()) * 1.3)


def _record_metrics(state, *, model_name: str, prompt_tokens: int, completion_tokens: int, duration_seconds: float, stream: bool, chat_id: str | None):
    total_tokens = prompt_tokens + completion_tokens
    tps = round((completion_tokens / duration_seconds), 2) if duration_seconds > 0 else 0.0
    metric = {
        "id": f"m-{uuid.uuid4().hex[:10]}",
        "created": int(time.time()),
        "model": model_name,
        "chat_id": chat_id,
        "stream": stream,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "duration_seconds": round(duration_seconds, 3),
        "tokens_per_sec": tps,
    }
    state.latest_metrics = metric
    state.metrics_history.append(metric)
    if len(state.metrics_history) > 200:
        state.metrics_history = state.metrics_history[-200:]

    state.metrics_totals["requests"] += 1
    state.metrics_totals["prompt_tokens"] += prompt_tokens
    state.metrics_totals["completion_tokens"] += completion_tokens
    state.metrics_totals["total_tokens"] += total_tokens
    state.metrics_totals["total_seconds"] += duration_seconds

    return metric


def _create_chat(state, title: str | None = None):
    chat_id = f"chat_{uuid.uuid4().hex[:10]}"
    now = int(time.time())
    chat = {
        "id": chat_id,
        "title": title or "New Chat",
        "created": now,
        "updated": now,
        "messages": [],
    }
    state.chats[chat_id] = chat
    state.chat_order.insert(0, chat_id)
    state.active_chat_id = chat_id
    return chat


def _chat_summary(chat: dict):
    return {
        "id": chat["id"],
        "title": chat["title"],
        "created": chat["created"],
        "updated": chat["updated"],
        "message_count": len(chat.get("messages", [])),
    }


def _load_selected_model(model_key: str, hf_token: str | None = None):
    state = get_global_state()
    _set_loading_state(
        status="loading",
        model_key=model_key,
        stage="preparing",
        message="Preparing model metadata",
        progress=5,
    )

    try:
        info = PREDEFINED_MODELS[model_key]
        engine = info.get("engine", "transformers")
        model_name = info["model"]

        if engine != "ollama":
            _set_loading_state(
                status="loading",
                model_key=model_key,
                stage="auth",
                message="Checking Hugging Face credentials",
                progress=12,
            )
            token = _resolve_hf_token(hf_token)
            if token:
                from huggingface_hub import login
                login(token)

        if engine == "transformers":
            _set_loading_state(
                status="loading",
                model_key=model_key,
                stage="initializing",
                message="Initializing Transformers adapter",
                progress=25,
            )
            from openrun.adapters.huggingface import HuggingFaceAdapter
            quantize = state.config.quantize if state.config else None
            low_cpu_mem = state.config.low_cpu_mem if state.config else False
            adapter = HuggingFaceAdapter(model_name, quantize=quantize, low_cpu_mem=low_cpu_mem)
        elif engine == "airllm":
            _set_loading_state(
                status="loading",
                model_key=model_key,
                stage="initializing",
                message="Initializing AirLLM adapter",
                progress=25,
            )
            from openrun.adapters.airllm import AirLLMAdapter
            adapter = AirLLMAdapter(model_name)
        else:
            _set_loading_state(
                status="loading",
                model_key=model_key,
                stage="connecting",
                message="Connecting to local Ollama runtime",
                progress=25,
            )
            from openrun.adapters.ollama import OllamaAdapter
            adapter = OllamaAdapter(model_name)

        _set_loading_state(
            status="loading",
            model_key=model_key,
            stage="loading_weights",
            message="Loading model weights into memory",
            progress=60,
        )

        adapter.load()
        state.adapter = adapter

        if state.config:
            state.config.model = model_name

        _set_loading_state(
            status="ready",
            model_key=model_key,
            stage="ready",
            message="Model ready for chat",
            progress=100,
            error=None,
        )
    except Exception as e:
        _set_loading_state(
            status="error",
            model_key=model_key,
            stage="failed",
            message="Model load failed",
            progress=100,
            error=str(e),
        )


@router.get("/models")
@router.get("/v1/models")
async def list_models(request: Request):
    state = get_global_state()
    current_model = None
    if state.adapter and hasattr(state.adapter, "model_name"):
        current_model = state.adapter.model_name
    elif state.config and state.config.model:
        current_model = state.config.model

    # Dynamically build base API URL and fetch configured API key (if any)
    base_url_str = str(request.base_url).rstrip("/")
    api_base_url = f"{base_url_str}/v1"
    from urllib.parse import quote

    data = []
    base_chat_domain = "https://openrun-web.vercel.app/"
    base_params = f"{base_chat_domain}?url={quote(api_base_url)}&theme=dark"
    for key, info in PREDEFINED_MODELS.items():
        share_url = f"{base_params}&model={quote(key)}"

        data.append({
            "id": key,
            "object": "model",
            "engine": info.get("engine", "transformers"),
            "name": info.get("model"),
            "size": info.get("size", "N/A"),
            "context": info.get("context", "N/A"),
            "speed": info.get("speed", "N/A"),
            "loaded": current_model == info.get("model"),
            "url": share_url,
        })

    return {
        "object": "list",
        "data": data,
        "loading": _loading_snapshot(state),
    }


@router.get("/models/status")
@router.get("/v1/models/status")
async def model_loading_status():
    state = get_global_state()
    loaded_model = None
    if state.adapter and hasattr(state.adapter, "model_name"):
        loaded_model = state.adapter.model_name
    elif state.config:
        loaded_model = state.config.model

    return {
        **_loading_snapshot(state),
        "loaded_model": loaded_model,
    }


@router.get("/models/catalog")
@router.get("/v1/models/catalog")
async def model_catalog(request: Request):
    try:
        from openrun.models.registry import load_dynamic_models
        load_dynamic_models()
    except Exception:
        pass
    base_url_str = str(request.base_url).rstrip("/")
    api_base_url = f"{base_url_str}/v1"
    from urllib.parse import quote
    
    data = []
    base_chat_domain = "https://openrun-web.vercel.app/"
    base_params = f"{base_chat_domain}?url={quote(api_base_url)}&theme=dark"
    for key, info in PREDEFINED_MODELS.items():
        share_url = f"{base_params}&model={quote(key)}"

        data.append({
            "id": key,
            "object": "model",
            "engine": info.get("engine", "transformers"),
            "name": info.get("model"),
            "size": info.get("size", "N/A"),
            "context": info.get("context", "N/A"),
            "speed": info.get("speed", "N/A"),
            "url": share_url,
        })
    return {
        "object": "list",
        "data": data,
    }


@router.post("/models/load", dependencies=[Depends(verify_api_key)])
@router.post("/v1/models/load", dependencies=[Depends(verify_api_key)])
async def load_model_from_ui(payload: dict):
    model_key = (payload or {}).get("model_key")
    hf_token = (payload or {}).get("hf_token")

    if not model_key or model_key not in PREDEFINED_MODELS:
        return {
            "ok": False,
            "error": "Invalid model_key",
        }

    state = get_global_state()
    if state.loading_status == "loading":
        return {
            "ok": False,
            "error": "Another model is currently loading",
            "loading_model": state.loading_model_key,
        }

    _set_loading_state(
        status="queued",
        model_key=model_key,
        stage="queued",
        message="Queued for loading",
        progress=0,
        error=None,
    )

    thread = threading.Thread(target=_load_selected_model, args=(model_key, hf_token), daemon=True)
    thread.start()

    return {
        "ok": True,
        "status": "queued",
        "model_key": model_key,
        "stage": "queued",
        "message": "Queued for loading",
    }


@router.get("/v1/chats", dependencies=[Depends(verify_api_key)])
async def list_chats():
    state = get_global_state()
    chats = [_chat_summary(state.chats[cid]) for cid in state.chat_order if cid in state.chats]
    return {
        "object": "list",
        "data": chats,
        "active_chat_id": state.active_chat_id,
    }


@router.post("/v1/chats", dependencies=[Depends(verify_api_key)])
async def create_chat(payload: dict | None = None):
    state = get_global_state()
    title = (payload or {}).get("title")
    chat = _create_chat(state, title=title)
    return {"ok": True, "chat": chat}


@router.get("/v1/chats/{chat_id}", dependencies=[Depends(verify_api_key)])
async def get_chat(chat_id: str):
    state = get_global_state()
    chat = state.chats.get(chat_id)
    if not chat:
        return {"ok": False, "error": "Chat not found"}
    state.active_chat_id = chat_id
    return {"ok": True, "chat": chat}


@router.patch("/v1/chats/{chat_id}", dependencies=[Depends(verify_api_key)])
async def rename_chat(chat_id: str, payload: dict):
    state = get_global_state()
    chat = state.chats.get(chat_id)
    if not chat:
        return {"ok": False, "error": "Chat not found"}
    title = (payload or {}).get("title", "").strip()
    if title:
        chat["title"] = title[:80]
    chat["updated"] = int(time.time())
    return {"ok": True, "chat": chat}


@router.delete("/v1/chats/{chat_id}", dependencies=[Depends(verify_api_key)])
async def delete_chat(chat_id: str):
    state = get_global_state()
    if chat_id not in state.chats:
        return {"ok": False, "error": "Chat not found"}
    del state.chats[chat_id]
    state.chat_order = [cid for cid in state.chat_order if cid != chat_id]
    if state.active_chat_id == chat_id:
        state.active_chat_id = state.chat_order[0] if state.chat_order else None
    return {"ok": True}


@router.get("/v1/metrics/live", dependencies=[Depends(verify_api_key)])
async def live_metrics():
    state = get_global_state()
    return {
        "ok": True,
        "data": state.latest_metrics,
    }


@router.get("/v1/metrics/history", dependencies=[Depends(verify_api_key)])
async def metrics_history(limit: int = 20):
    state = get_global_state()
    safe_limit = max(1, min(200, int(limit)))
    return {
        "ok": True,
        "data": state.metrics_history[-safe_limit:],
    }


@router.get("/v1/metrics/summary", dependencies=[Depends(verify_api_key)])
async def metrics_summary():
    state = get_global_state()
    totals = state.metrics_totals
    avg_tps = round((totals["completion_tokens"] / totals["total_seconds"]), 2) if totals["total_seconds"] > 0 else 0.0
    return {
        "ok": True,
        "totals": totals,
        "avg_tokens_per_sec": avg_tps,
        "latest": state.latest_metrics,
    }

@router.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
@router.post("/v1/chat/completions/chat/completions", dependencies=[Depends(verify_api_key)])
async def chat_completions(request: ChatRequest):
    # Acquire semaphore to prevent concurrent GPU inference (OOM protection)
    acquired = _inference_semaphore.locked()
    if acquired:
        # Another request is already running — check if we can wait briefly
        try:
            await asyncio.wait_for(_inference_semaphore.acquire(), timeout=120.0)
        except asyncio.TimeoutError:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "message": "Server is busy processing another request. Please retry shortly.",
                        "type": "server_busy",
                    }
                },
            )
    else:
        await _inference_semaphore.acquire()

    try:
        return await _run_chat_completions(request)
    finally:
        _inference_semaphore.release()


async def _run_chat_completions(request: ChatRequest):
    state = get_global_state()
    
    # Precedence: config.model > request.model > "openrun"
    model_name = getattr(state.config, "model", None) or request.model or "openrun"
    
    # Extract messages directly
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # Log incoming messages for easy developer debugging and diagnostic visibility
    print(f"\n\033[94m📥 Incoming API Messages (Turns: {len(messages)}):\033[0m")
    for m in messages:
        role_color = "\033[93m" if m["role"] == "user" else ("\033[95m" if m["role"] == "system" else "\033[92m")
        print(f"  {role_color}[{m['role']}]:\033[0m {m['content']}")
    print()

    prompt_tokens = sum(_estimate_tokens(state, m["content"]) for m in messages)

    chat_id = request.chat_id
    if chat_id:
        if chat_id not in state.chats:
            created_chat = _create_chat(state, title="New Chat")
            chat_id = created_chat["id"]
        state.active_chat_id = chat_id

    def _persist_chat_and_metrics(response_text: str, stream_mode: bool, duration_seconds: float, finish_reason: str = "stop"):
        completion_tokens = _estimate_tokens(state, response_text)
        metric = _record_metrics(
            state,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            duration_seconds=duration_seconds,
            stream=stream_mode,
            chat_id=chat_id,
        )
        if chat_id and chat_id in state.chats:
            user_messages = [
                {"role": "user", "content": m["content"]}
                for m in messages
                if m.get("role") == "user"
            ]
            chat = state.chats[chat_id]
            chat["messages"] = user_messages + [{"role": "assistant", "content": response_text}]
            chat["updated"] = int(time.time())
            if chat["title"] == "New Chat" and user_messages:
                chat["title"] = user_messages[0]["content"][:48] or "New Chat"
        return metric

    if request.stream:
        def _on_stream_complete(response_text: str, finish_reason: str, elapsed: float):
            _persist_chat_and_metrics(response_text, True, elapsed, finish_reason)

        return StreamingResponse(
            stream_response(messages, model_name=model_name, on_complete=_on_stream_complete),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    # Call inference layer
    started_at = time.time()
    response_text = generate_response(messages)
    completion_tokens = _estimate_tokens(state, response_text)
    metric = _persist_chat_and_metrics(response_text, False, time.time() - started_at)
        
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        },
        "chat_id": chat_id,
        "metrics": metric,
    }
