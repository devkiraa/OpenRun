PREDEFINED_MODELS = {
    # ⚡ Transformers Models
    "qwen": {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "engine": "transformers",
        "type": "balanced",
        "size": "7B",
        "context": "128k",
        "speed": "30-40 t/s"
    },
    "phi": {
        "model": "microsoft/Phi-3-mini-4k-instruct",
        "engine": "transformers",
        "type": "fast",
        "size": "3.8B",
        "context": "4k",
        "speed": "50-60 t/s"
    },
    "mistral": {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "engine": "transformers",
        "type": "balanced",
        "size": "7.3B",
        "context": "32k",
        "speed": "30-40 t/s"
    },
    "deepseek": {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "engine": "transformers",
        "type": "balanced",
        "size": "8B",
        "context": "128k",
        "speed": "30-35 t/s"
    },
    
    # 🧠 AirLLM Models
    "llama3": {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "engine": "airllm",
        "type": "large",
        "size": "8B",
        "context": "8k",
        "speed": "25-30 t/s"
    },
    "llama70b": {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "engine": "airllm",
        "type": "massive",
        "size": "70B",
        "context": "8k",
        "speed": "0.1-1 t/s"
    },
    
    # 🦙 Ollama Models
    "gemma": {
        "model": "gemma:7b",
        "engine": "ollama",
        "type": "ollama",
        "size": "8.5B",
        "context": "8k",
        "speed": "20-30 t/s"
    },
    "gemma2:2b": {
        "model": "gemma2:2b",
        "engine": "ollama",
        "type": "ollama",
        "size": "2.6B",
        "context": "8k",
        "speed": "60-70 t/s"
    },
    "llama3-ollama": {
        "model": "llama3:8b",
        "engine": "ollama",
        "type": "ollama",
        "size": "8B",
        "context": "8k",
        "speed": "30-35 t/s"
    }
}