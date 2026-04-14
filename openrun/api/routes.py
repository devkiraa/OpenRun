from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openrun.api.schemas import ChatRequest
from openrun.core.state import get_global_state
from openrun.api.dependencies import verify_api_key
from openrun.model.inference import generate_response, stream_response
import time
import uuid

router = APIRouter()

@router.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
async def chat_completions(request: ChatRequest):
    state = get_global_state()
    
    # Precedence: config.model > request.model > "openrun"
    model_name = getattr(state.config, "model", None) or request.model or "openrun"
    
    # Extract messages directly
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    if request.stream:
        return StreamingResponse(
            stream_response(messages),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )

    # Call inference layer
    response_text = generate_response(messages)
    
    # Calculate token usage (exact if tokenizer available, else approximate)
    prompt_tokens = 0
    completion_tokens = 0
    
    if hasattr(state, "adapter") and hasattr(state.adapter, "tokenizer") and hasattr(state.adapter.tokenizer, "encode"):
        prompt_tokens = sum(len(state.adapter.tokenizer.encode(m["content"])) for m in messages)
        completion_tokens = len(state.adapter.tokenizer.encode(response_text))
    else:
        # 1 word ~ 1.3 tokens heuristic
        prompt_tokens = int(sum(len(m["content"].split()) * 1.3 for m in messages))
        completion_tokens = int(len(response_text.split()) * 1.3)
        
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
        }
    }
