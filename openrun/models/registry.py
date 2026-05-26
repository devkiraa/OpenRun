PREDEFINED_MODELS = {
    # ⚡ Transformers Models
    # --- DeepSeek Series ---
    "deepseek-r1-8b": {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "engine": "transformers",
        "type": "balanced",
        "size": "8B",
        "context": "128k",
        "speed": "30-35 t/s",
        "vram": "~9 GB",
        "best_for": "Top-tier academic and logical reasoning"
    },
    "deepseek-r1-1.5b": {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        "engine": "transformers",
        "type": "fast",
        "size": "1.5B",
        "context": "32k",
        "speed": "~90+ t/s",
        "vram": "~3.5 GB",
        "best_for": "A fantastic middle ground of speed and strong multilingual/coding capabilities."
    },
    "deepseek-r1-14b": {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        "engine": "transformers",
        "type": "large",
        "size": "14B",
        "context": "128k",
        "speed": "15-20 t/s",
        "vram": "~15 GB",
        "best_for": "Highly complex logical & math problems"
    },
    "deepseek-coder-v2-lite": {
        "model": "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
        "engine": "transformers",
        "type": "large",
        "size": "16B (MoE)",
        "context": "128k",
        "speed": "15-22 t/s",
        "vram": "~12 GB",
        "best_for": "Efficient coding and threat intelligence logic"
    },

    # --- Llama Series ---
    "llama3.1-8b": {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "engine": "transformers",
        "type": "balanced",
        "size": "8B",
        "context": "128k",
        "speed": "30-35 t/s",
        "vram": "~8.5 GB",
        "best_for": "The industry standard baseline; general instruction tuning"
    },
    "llama3.2-3b": {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "engine": "transformers",
        "type": "fast",
        "size": "3B",
        "context": "128k",
        "speed": "~60+ t/s",
        "vram": "~4.5 GB",
        "best_for": "The smartest model you can run on a T4 while still staying above 50 tokens/sec."
    },
    "llama3.2-1b": {
        "model": "meta-llama/Llama-3.2-1B-Instruct",
        "engine": "transformers",
        "type": "ultra-fast",
        "size": "1B",
        "context": "128k",
        "speed": "~120+ t/s",
        "vram": "~3 GB",
        "best_for": "Meta's ultra-lightweight model. Excellent for fast agentic reasoning and on-device logic."
    },

    # --- Qwen Series ---
    "qwen3-8b": {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "engine": "transformers",
        "type": "balanced",
        "size": "7B",
        "context": "128k",
        "speed": "30-40 t/s",
        "vram": "~8 GB",
        "best_for": "Multilingual support; fast processing; instruction following"
    },
    "qwen3-coder-7b": {
        "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "engine": "transformers",
        "type": "balanced",
        "size": "7B",
        "context": "128k",
        "speed": "30-40 t/s",
        "vram": "~7.5 GB",
        "best_for": "Autonomous coding tasks; script generation; log parsing"
    },
    "qwen3-1.5b": {
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "engine": "transformers",
        "type": "fast",
        "size": "1.5B",
        "context": "32k",
        "speed": "~90+ t/s",
        "vram": "~3.5 GB",
        "best_for": "A fantastic middle ground of speed and strong multilingual/coding capabilities."
    },
    "qwen3-0.5b": {
        "model": "Qwen/Qwen2.5-0.5B-Instruct",
        "engine": "transformers",
        "type": "ultra-fast",
        "size": "0.5B",
        "context": "32k",
        "speed": "~180+ t/s",
        "vram": "~2 GB",
        "best_for": "The absolute fastest. Great for basic routing, simple formatting, and micro-tasks."
    },

    # --- Gemma Series ---
    "gemma3-4b": {
        "model": "google/gemma-2-9b-it",
        "engine": "transformers",
        "type": "balanced",
        "size": "9B",
        "context": "8k",
        "speed": "25-35 t/s",
        "vram": "~6 GB",
        "best_for": "General text tasks with a highly dense architecture"
    },
    "gemma3-1b": {
        "model": "google/gemma-2-2b-it",
        "engine": "transformers",
        "type": "fast",
        "size": "2.6B",
        "context": "8k",
        "speed": "~75+ t/s",
        "vram": "~3 GB",
        "best_for": "Google's dense architectures. Exceptional at instruction following and logic puzzles for their size."
    },

    # --- Phi Series ---
    "phi-4-mini": {
        "model": "microsoft/phi-4-mini-instruct",
        "engine": "transformers",
        "type": "fast",
        "size": "3.8B",
        "context": "4k",
        "speed": "50-60 t/s",
        "vram": "~5 GB",
        "best_for": "Logic-heavy tasks in constrained spaces"
    },
    "phi3-medium": {
        "model": "microsoft/Phi-3-medium-128k-instruct",
        "engine": "transformers",
        "type": "balanced",
        "size": "14B",
        "context": "128k",
        "speed": "15-20 t/s",
        "vram": "~10 GB",
        "best_for": "Logic and general instruction in memory restricted systems"
    },

    # --- Mistral Series ---
    "mistral-nemo": {
        "model": "mistralai/Mistral-Nemo-Instruct-2407",
        "engine": "transformers",
        "type": "large",
        "size": "12B",
        "context": "128k",
        "speed": "20-25 t/s",
        "vram": "~13 GB",
        "best_for": "Advanced general tasks (Requires strict memory management)"
    },
    "star-coder-2-7b": {
        "model": "bigcode/starcoder2-7b",
        "engine": "transformers",
        "type": "balanced",
        "size": "7B",
        "context": "16k",
        "speed": "30-40 t/s",
        "vram": "~8 GB",
        "best_for": "Code completion and repository-level context tasks"
    },
    "star-coder-2-3b": {
        "model": "bigcode/starcoder2-3b",
        "engine": "transformers",
        "type": "fast",
        "size": "3B",
        "context": "16k",
        "speed": "~60+ t/s",
        "vram": "~5 GB",
        "best_for": "The fastest specialized coding and autocomplete model for the T4."
    },

    # --- Backward-Compatibility Aliases ---
    "qwen": {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "engine": "transformers",
        "type": "balanced",
        "size": "7B",
        "context": "128k",
        "speed": "30-40 t/s",
        "vram": "~8 GB",
        "best_for": "Multilingual support; fast processing"
    },
    "phi": {
        "model": "microsoft/Phi-3-mini-4k-instruct",
        "engine": "transformers",
        "type": "fast",
        "size": "3.8B",
        "context": "4k",
        "speed": "50-60 t/s",
        "vram": "~5 GB",
        "best_for": "Lightweight general task logic"
    },
    "mistral": {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "engine": "transformers",
        "type": "balanced",
        "size": "7.3B",
        "context": "32k",
        "speed": "30-40 t/s",
        "vram": "~8 GB",
        "best_for": "Robust balanced general instruction"
    },
    "deepseek": {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "engine": "transformers",
        "type": "balanced",
        "size": "8B",
        "context": "128k",
        "speed": "30-35 t/s",
        "vram": "~9 GB",
        "best_for": "Top-tier academic and logical reasoning"
    },

    # 🧠 AirLLM Models
    "llama3-8b": {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "engine": "airllm",
        "type": "large",
        "size": "8B",
        "context": "8k",
        "speed": "25-30 t/s",
        "vram": "~8.5 GB",
        "best_for": "General instruction baseline on limited systems"
    },
    "llama3-70b": {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "engine": "airllm",
        "type": "massive",
        "size": "70B",
        "context": "8k",
        "speed": "0.1-1 t/s",
        "vram": "~40 GB",
        "best_for": "Ultra-complex reasoning on multiple/large GPUs"
    },
    "llama3": {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "engine": "airllm",
        "type": "large",
        "size": "8B",
        "context": "8k",
        "speed": "25-30 t/s",
        "vram": "~8.5 GB",
        "best_for": "General instruction baseline"
    },
    "llama70b": {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "engine": "airllm",
        "type": "massive",
        "size": "70B",
        "context": "8k",
        "speed": "0.1-1 t/s",
        "vram": "~40 GB",
        "best_for": "Ultra-complex reasoning"
    },

    # 🦙 Ollama Models
    "gemma": {
        "model": "gemma:7b",
        "engine": "ollama",
        "type": "ollama",
        "size": "8.5B",
        "context": "8k",
        "speed": "20-30 t/s",
        "vram": "~8 GB",
        "best_for": "General instruction following via Ollama"
    },
    "gemma2-2b": {
        "model": "gemma2:2b",
        "engine": "ollama",
        "type": "ollama",
        "size": "2.6B",
        "context": "8k",
        "speed": "~75+ t/s",
        "vram": "~3 GB",
        "best_for": "Google's dense architectures. Exceptional at instruction following and logic puzzles for their size."
    },
    "gemma2:2b": {
        "model": "gemma2:2b",
        "engine": "ollama",
        "type": "ollama",
        "size": "2.6B",
        "context": "8k",
        "speed": "~75+ t/s",
        "vram": "~3 GB",
        "best_for": "Google's dense architectures. Exceptional at instruction following and logic puzzles for their size."
    },
    "llama3-ollama": {
        "model": "llama3:8b",
        "engine": "ollama",
        "type": "ollama",
        "size": "8B",
        "context": "8k",
        "speed": "30-35 t/s",
        "vram": "~8.5 GB",
        "best_for": "Standard baseline model via Ollama"
    }
}