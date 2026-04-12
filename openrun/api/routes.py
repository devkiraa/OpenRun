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
    model_name = state.config.model if state.config and state.config.model else request.model
    model_name = model_name or "openrun"
    
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
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }
