from openrun.core.config import Config
from openrun.core.state import get_global_state

def load_model(config: Config):
    adapter = None
    
    # 1. Routing based on Engine or File Type
    if config.engine == "vllm":
        from openrun.adapters.vllm_adapter import VLLMAdapter
        adapter = VLLMAdapter(config.model)
    elif config.engine == "llamacpp" or (config.file and config.file.lower().endswith(".gguf")):
        from openrun.adapters.llamacpp import LlamaCppAdapter
        adapter = LlamaCppAdapter(config.file or config.model)
    elif config.engine == "ollama":
        from openrun.adapters.ollama import OllamaAdapter
        adapter = OllamaAdapter(config.model)
    elif config.file and config.file.endswith(".py"):
        from openrun.adapters.custom import CustomAdapter
        adapter = CustomAdapter(config.file)
    elif config.model:
        # Default to HuggingFace (Transformers)
        from openrun.adapters.huggingface import HuggingFaceAdapter
        adapter = HuggingFaceAdapter(
            config.model, 
            quantize=config.quantize, 
            low_cpu_mem=config.low_cpu_mem,
            draft_model_name=config.draft_model
        )
        try:
            adapter.load()
        except RuntimeError as e:
            if "Gated Repository" in str(e):
                raise
            print("\033[93m⚠️ Memory limited! Switching to AirLLM engine...\033[0m")
            print("\033[93m⏳ Expect slower responses (10-60 seconds)\033[0m")
            from openrun.adapters.airllm import AirLLMAdapter
            adapter = AirLLMAdapter(config.model)
            adapter.load()
        
        # We skip the second adapter.load() at the end if we already loaded it here
        # but the current structure calls it again. Let's fix the structure.
        state = get_global_state()
        state.adapter = adapter
        print("Model loaded successfully.")
        return
    else:
        print("Warning: Neither --model nor --file specified. Running in dummy mode.")
        return
        
    adapter.load()
    
    # Store adapter in global state
    state = get_global_state()
    state.adapter = adapter
    print("Model loaded successfully.")
