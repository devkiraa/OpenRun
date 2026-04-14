PREDEFINED_MODELS = {
    # ⚡ Fast models
    "qwen": {
        "model": "Qwen/Qwen2.5-3B-Instruct",
        "engine": "transformers",
        "type": "fast"
    },
    "phi": {
        "model": "microsoft/Phi-3-mini-4k-instruct",
        "engine": "transformers",
        "type": "fast"
    },
    
    # ⚖️ Balanced models
    "mistral": {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "engine": "transformers",
        "type": "balanced"
    },
    "deepseek": {
        "model": "deepseek-ai/deepseek-coder-6.7b-instruct",
        "engine": "transformers",
        "type": "balanced"
    },
    
    # 🧠 Large models (AirLLM)
    "llama3": {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "engine": "airllm",
        "type": "large"
    },
    "llama70b": {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "engine": "airllm",
        "type": "large"
    }
}