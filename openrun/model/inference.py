from openrun.core.state import get_global_state
import json

def stream_response(messages: list):
    state = get_global_state()

    if not hasattr(state, "adapter") or not state.adapter:
        yield "data: [ERROR] No model loaded\n\n"
        return

    try:
        # Initial role chunk
        yield f"data: {json.dumps({'id': 'chatcmpl-openrun', 'object': 'chat.completion.chunk', 'choices': [{'delta': {'role': 'assistant'}}]})}\n\n"

        # Content chunks
        for chunk in state.adapter.stream(messages):
            yield f"data: {json.dumps({'id': 'chatcmpl-openrun', 'object': 'chat.completion.chunk', 'choices': [{'delta': {'content': chunk}}]})}\n\n"

        # Finish reason chunk
        yield f"data: {json.dumps({'id': 'chatcmpl-openrun', 'object': 'chat.completion.chunk', 'choices': [{'finish_reason': 'stop'}]})}\n\n"
        
        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

def generate_response(messages: list) -> str:
    state = get_global_state()
    
    if not hasattr(state, "adapter") or not state.adapter:
        return "Warning: No model loaded. Please provide --model or --file."
    
    try:
        return state.adapter.generate(messages)
    except Exception as e:
        return f"Error: Model generation failed - {str(e)}"
