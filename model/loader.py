from core.config import Config
from core.state import get_global_state

def load_model(config: Config):
    adapter = None
    
    if config.file:
        from adapters.custom import CustomAdapter
        adapter = CustomAdapter(config.file)
    elif config.model:
        from adapters.huggingface import HuggingFaceAdapter
        adapter = HuggingFaceAdapter(config.model)
    else:
        print("Warning: Neither --model nor --file specified. Running in dummy mode.")
        return
        
    adapter.load()
    
    # Store adapter in global state
    state = get_global_state()
    state.adapter = adapter
    print("Model loaded successfully.")
