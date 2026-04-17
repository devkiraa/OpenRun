from openrun.core.state import get_global_state
import asyncio
import json
import time
import uuid


def _sse_chunk(chunk_id: str, created: int, model_name: str, delta: dict | None = None, finish_reason: str | None = None):
    payload = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_name,
        "choices": [{
            "index": 0,
            "delta": delta or {},
            "finish_reason": finish_reason,
        }],
    }
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _normalize_chunk(raw_chunk):
    if raw_chunk is None:
        return ""
    if isinstance(raw_chunk, bytes):
        return raw_chunk.decode("utf-8", errors="ignore")
    if isinstance(raw_chunk, str):
        return raw_chunk
    return str(raw_chunk)


def _coalesce_chunks(raw_iterable, min_emit_chars: int = 3, max_buffer_chars: int = 64):
    """Coalesce tiny token fragments so SSE clients render smoother text."""
    buffer = ""
    boundaries = set(" \n\t.,;:!?)]}\"'`")

    for raw in raw_iterable:
        part = _normalize_chunk(raw)
        if not part:
            continue
        buffer += part

        # Emit if buffer is large enough and has a natural boundary near the end.
        if len(buffer) >= min_emit_chars:
            last_boundary = -1
            scan_start = max(0, len(buffer) - 24)
            for idx in range(scan_start, len(buffer)):
                if buffer[idx] in boundaries:
                    last_boundary = idx

            if last_boundary != -1:
                emit = buffer[: last_boundary + 1]
                buffer = buffer[last_boundary + 1 :]
                if emit:
                    yield emit
                continue

        if len(buffer) >= max_buffer_chars:
            yield buffer
            buffer = ""

    if buffer:
        yield buffer


def stream_response(messages: list, model_name: str = "openrun", on_complete=None):
    state = get_global_state()

    if not hasattr(state, "adapter") or not state.adapter:
        yield f"data: {json.dumps({'error': {'message': 'No model loaded', 'type': 'invalid_request_error'}})}\n\n"
        yield "data: [DONE]\n\n"
        return

    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())
    finish_reason = "stop"
    started_at = time.time()
    full_text = ""

    try:
        # Initial role chunk
        yield _sse_chunk(chunk_id, created, model_name, delta={"role": "assistant"})

        # Content chunks with coalescing for smoother UI updates.
        for chunk in _coalesce_chunks(state.adapter.stream(messages)):
            full_text += chunk
            yield _sse_chunk(chunk_id, created, model_name, delta={"content": chunk})

    except (asyncio.CancelledError, GeneratorExit):
        finish_reason = "cancelled"
    except KeyboardInterrupt:
        finish_reason = "cancelled"
    except Exception as e:
        finish_reason = "error"
        yield f"data: {json.dumps({'error': {'message': str(e), 'type': 'stream_error'}}, ensure_ascii=False)}\n\n"
    finally:
        if on_complete:
            try:
                on_complete(full_text, finish_reason, time.time() - started_at)
            except Exception:
                pass
        # Send an explicit finish reason for clients that read terminal event chunks.
        yield _sse_chunk(chunk_id, created, model_name, finish_reason=finish_reason)
        yield "data: [DONE]\n\n"

def generate_response(messages: list) -> str:
    state = get_global_state()
    
    if not hasattr(state, "adapter") or not state.adapter:
        return "Warning: No model loaded. Please provide --model or --file."
    
    try:
        return state.adapter.generate(messages)
    except Exception as e:
        return f"Error: Model generation failed - {str(e)}"
