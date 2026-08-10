PREDEFINED_MODELS = {
    # ⚡ Transformers Models
    # --- DeepSeek Series ---
    "deepseek-1.5b": {'model': 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B', 'engine': 'transformers', 'type': 'fast', 'size': '1.5B', 'context': '32k', 'speed': '~90+ t/s', 'vram': '~4 GB', 'best_for': 'A fantastic middle ground of speed and distilled logic.'},
    "deepseek-7b": {'model': 'deepseek-ai/DeepSeek-R1-Distill-Qwen-7B', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '128k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Strong reasoning distilled from DeepSeek core.'},
    "deepseek-8b": {'model': 'deepseek-ai/DeepSeek-R1-Distill-Llama-8B', 'engine': 'transformers', 'type': 'balanced', 'size': '8B', 'context': '128k', 'speed': '25-30 t/s', 'vram': '~8.5 GB (8-bit)', 'best_for': 'Top-tier academic and mathematical reasoning.'},
    "deepseek-14b": {'model': 'deepseek-ai/DeepSeek-R1-Distill-Qwen-14B', 'engine': 'transformers', 'type': 'large', 'size': '14B', 'context': '128k', 'speed': '15-20 t/s', 'vram': '~10 GB (4-bit)', 'best_for': 'Highly complex logical problems. The T4 ceiling.'},
    "deepseek-coder-lite": {'model': 'deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct', 'engine': 'transformers', 'type': 'large', 'size': '16B', 'context': '128k', 'speed': '15-20 t/s', 'vram': '~12 GB (4-bit)', 'best_for': 'Efficient Mixture-of-Experts (MoE) coding architecture.'},

    # --- Llama Series ---
    "llama3.2-1b": {'model': 'meta-llama/Llama-3.2-1B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '1B', 'context': '128k', 'speed': '~120+ t/s', 'vram': '~3.5 GB', 'best_for': "Meta's fastest agentic reasoning and on-device logic."},
    "llama3.2-3b": {'model': 'meta-llama/Llama-3.2-3B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '3B', 'context': '128k', 'speed': '~60+ t/s', 'vram': '~6.5 GB', 'best_for': 'The smartest model while staying above 50 tokens/sec.'},
    "llama3.1-8b": {'model': 'meta-llama/Llama-3.1-8B-Instruct', 'engine': 'transformers', 'type': 'balanced', 'size': '8B', 'context': '128k', 'speed': '25-30 t/s', 'vram': '~8.5 GB (8-bit)', 'best_for': 'The industry standard baseline for general instruction.'},
    "llama3.2-11b-vl": {'model': 'meta-llama/Llama-3.2-11B-Vision-Instruct', 'engine': 'transformers', 'type': 'large', 'size': '11B', 'context': '128k', 'speed': '15-20 t/s', 'vram': '~8 GB (4-bit)', 'best_for': "Meta's flagship vision model. Needs strict 4-bit loading."},

    # --- Qwen Series ---
    "qwen2.5-0.5b": {'model': 'Qwen/Qwen2.5-0.5B-Instruct', 'engine': 'transformers', 'type': 'ultra-fast', 'size': '0.5B', 'context': '32k', 'speed': '~150+ t/s', 'vram': '~2 GB', 'best_for': 'The absolute fastest basic logic and formatting.'},
    "qwen2.5-coder-0.5b": {'model': 'Qwen/Qwen2.5-Coder-0.5B-Instruct', 'engine': 'transformers', 'type': 'ultra-fast', 'size': '0.5B', 'context': '32k', 'speed': '~150+ t/s', 'vram': '~2 GB', 'best_for': 'Rapid syntax checking and micro-script generation.'},
    "qwen2.5-1.5b": {'model': 'Qwen/Qwen2.5-1.5B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '1.5B', 'context': '32k', 'speed': '~90+ t/s', 'vram': '~4 GB', 'best_for': 'Highly capable text generation and knowledge retrieval.'},
    "qwen2.5-coder-1.5b": {'model': 'Qwen/Qwen2.5-Coder-1.5B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '1.5B', 'context': '32k', 'speed': '~90+ t/s', 'vram': '~4 GB', 'best_for': 'Quick code autocomplete and simple refactoring.'},
    "qwen2.5-math-1.5b": {'model': 'Qwen/Qwen2.5-Math-1.5B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '1.5B', 'context': '4k', 'speed': '~90+ t/s', 'vram': '~4 GB', 'best_for': 'Solving arithmetic and structured numerical tables.'},
    "qwen2.5-3b": {'model': 'Qwen/Qwen2.5-3B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '3B', 'context': '32k', 'speed': '~60+ t/s', 'vram': '~6.5 GB', 'best_for': 'Strong multilingual support and balanced speed.'},
    "qwen2.5-coder-3b": {'model': 'Qwen/Qwen2.5-Coder-3B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '3B', 'context': '32k', 'speed': '~60+ t/s', 'vram': '~6.5 GB', 'best_for': 'Mid-tier autonomous coding and backend logic.'},
    "qwen2.5-vl-3b": {'model': 'Qwen/Qwen2.5-VL-3B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '3B', 'context': '32k', 'speed': '~50+ t/s', 'vram': '~7 GB', 'best_for': 'Fast image processing, OCR, and visual parsing.'},
    "qwen2.5-omni-3b": {'model': 'Qwen/Qwen2.5-Omni-3B', 'engine': 'transformers', 'type': 'fast', 'size': '3B', 'context': '32k', 'speed': '~50+ t/s', 'vram': '~7 GB', 'best_for': 'Fast any-to-any multimodal reasoning (audio/text/image).'},
    "qwen2.5-7b": {'model': 'Qwen/Qwen2.5-7B-Instruct', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '128k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Robust multilingual support and huge active knowledge.'},
    "qwen2.5-coder-7b": {'model': 'Qwen/Qwen2.5-Coder-7B-Instruct', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '128k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Autonomous coding tasks and advanced script parsing.'},
    "qwen2.5-math-7b": {'model': 'Qwen/Qwen2.5-Math-7B-Instruct', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '4k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Parsing complex algorithms and strict logic outputs.'},
    "qwen2.5-vl-7b": {'model': 'Qwen/Qwen2.5-VL-7B-Instruct', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '32k', 'speed': '20-25 t/s', 'vram': '~8.5 GB (8-bit)', 'best_for': 'High-end vision reasoning and UI interface reading.'},
    "qwen2.5-14b": {'model': 'Qwen/Qwen2.5-14B-Instruct', 'engine': 'transformers', 'type': 'large', 'size': '14B', 'context': '128k', 'speed': '15-20 t/s', 'vram': '~10 GB (4-bit)', 'best_for': 'Immense active knowledge and deep logic chains.'},
    "qwen2.5-coder-14b": {'model': 'Qwen/Qwen2.5-Coder-14B-Instruct', 'engine': 'transformers', 'type': 'large', 'size': '14B', 'context': '128k', 'speed': '15-20 t/s', 'vram': '~10 GB (4-bit)', 'best_for': 'Advanced full-stack application logic and debugging.'},

    # --- Gemma Series ---
    "gemma-4-e2b": {'model': 'google/gemma-4-E2B', 'engine': 'transformers', 'type': 'ultra-fast', 'size': '2B', 'context': '8k', 'speed': '~100+ t/s', 'vram': '~2.5 GB', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Base edge model optimized for local mobile execution."},
    "gemma-4-e2b-it": {'model': 'google/gemma-4-E2B-it', 'engine': 'transformers', 'type': 'ultra-fast', 'size': '2B', 'context': '8k', 'speed': '~100+ t/s', 'vram': '~2.5 GB', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Google's flagship ultra-lightweight edge model with native audio and vision."},
    "gemma-4-e2b-it-qat": {'model': 'google/gemma-4-E2B-it-qat-mobile-transformers', 'engine': 'transformers', 'type': 'ultra-fast', 'size': '2B', 'context': '8k', 'speed': '~100+ t/s', 'vram': '~2.5 GB', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Mobile Optimized QAT variant for direct on-device text/audio/vision tasks."},
    "gemma-4-e4b": {'model': 'google/gemma-4-E4B', 'engine': 'transformers', 'type': 'fast', 'size': '4B', 'context': '8k', 'speed': '~60+ t/s', 'vram': '~4.5 GB', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Base edge-optimized model for high-end phones and laptops."},
    "gemma-4-e4b-it": {'model': 'google/gemma-4-E4B-it', 'engine': 'transformers', 'type': 'fast', 'size': '4B', 'context': '8k', 'speed': '~60+ t/s', 'vram': '~4.5 GB', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Edge-optimized model for high-end phones and laptops with native audio/vision."},
    "gemma-4-12b": {'model': 'google/gemma-4-12B', 'engine': 'transformers', 'type': 'large', 'size': '12B', 'context': '8k', 'speed': '~20+ t/s', 'vram': '~8 GB (4-bit)', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Base unified multimodal encoder-free model."},
    "gemma-4-12b-it": {'model': 'google/gemma-4-12B-it', 'engine': 'transformers', 'type': 'large', 'size': '12B', 'context': '8k', 'speed': '~20+ t/s', 'vram': '~8 GB (4-bit)', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Unified multimodal encoder-free model, the workstation sweet-spot."},
    "gemma-4-26b-a4b": {'model': 'google/gemma-4-26B-A4B', 'engine': 'transformers', 'type': 'large', 'size': '26B', 'context': '8k', 'speed': '~15+ t/s', 'vram': '~16 GB (4-bit)', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Highly efficient Mixture-of-Experts (MoE) variant with 3.8B active parameters."},
    "gemma-4-31b": {'model': 'google/gemma-4-31B', 'engine': 'transformers', 'type': 'massive', 'size': '31B', 'context': '8k', 'speed': '~10+ t/s', 'vram': '~20 GB (4-bit)', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Flagship dense base model tailored for consumer GPUs."},
    "gemma-4-31b-it": {'model': 'google/gemma-4-31B-it', 'engine': 'transformers', 'type': 'massive', 'size': '31B', 'context': '8k', 'speed': '~10+ t/s', 'vram': '~20 GB (4-bit)', 'provider': 'Google', 'family': 'Gemma 4', 'best_for': "Flagship dense model maximizing reasoning, long-context, and planning."},
    "gemma2-2b": {'model': 'google/gemma-2-2b-it', 'engine': 'transformers', 'type': 'fast', 'size': '2.6B', 'context': '8k', 'speed': '~75+ t/s', 'vram': '~6 GB', 'best_for': "Google's dense architecture for logic puzzles."},
    "gemma2-9b": {'model': 'google/gemma-2-9b-it', 'engine': 'transformers', 'type': 'balanced', 'size': '9B', 'context': '8k', 'speed': '20-25 t/s', 'vram': '~10 GB (8-bit)', 'best_for': 'High-end general text tasks (hits above its weight class).'},
    "codegemma-7b": {'model': 'google/codegemma-7b-it', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '8k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': "Google's specialized instruction-following code model."},

    # --- Phi Series ---
    "phi3.5-mini": {'model': 'microsoft/Phi-3.5-mini-instruct', 'engine': 'transformers', 'type': 'fast', 'size': '3.8B', 'context': '128k', 'speed': '~50+ t/s', 'vram': '~8 GB', 'best_for': 'Logic-heavy tasks within constrained memory spaces.'},
    "phi4-mini": {'model': 'microsoft/Phi-4-mini-instruct', 'engine': 'transformers', 'type': 'fast', 'size': '3.8B', 'context': '128k', 'speed': '~50+ t/s', 'vram': '~8 GB', 'best_for': "Microsoft's latest reasoning-dense logic model."},
    "phi4-multimodal": {'model': 'microsoft/Phi-4-multimodal-instruct', 'engine': 'transformers', 'type': 'fast', 'size': '~4B', 'context': '128k', 'speed': '~45+ t/s', 'vram': '~8 GB', 'best_for': 'Audio and image reasoning in a single pass.'},

    # --- Mistral Series ---
    "mistral-v0.3": {'model': 'mistralai/Mistral-7B-Instruct-v0.3', 'engine': 'transformers', 'type': 'balanced', 'size': '7.3B', 'context': '32k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Excellent general instruction following.'},
    "mistral-nemo": {'model': 'mistralai/Mistral-Nemo-Instruct-2407', 'engine': 'transformers', 'type': 'large', 'size': '12B', 'context': '128k', 'speed': '15-20 t/s', 'vram': '~9 GB (4-bit)', 'best_for': 'Advanced general tasks with a massive context window.'},

    # --- Other/Additional Series ---
    "smollm2-135m": {'model': 'HuggingFaceTB/SmolLM2-135M-Instruct', 'engine': 'transformers', 'type': 'ultra-fast', 'size': '135M', 'context': '8k', 'speed': '~250+ t/s', 'vram': '~1 GB', 'best_for': 'Edge devices and extreme micro-tasks.'},
    "smollm2-360m": {'model': 'HuggingFaceTB/SmolLM2-360M-Instruct', 'engine': 'transformers', 'type': 'ultra-fast', 'size': '360M', 'context': '8k', 'speed': '~200+ t/s', 'vram': '~1.5 GB', 'best_for': 'Ultra-lightweight log parsing and routing.'},
    "olmo-1b": {'model': 'allenai/OLMo-1B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '1B', 'context': '2k', 'speed': '~120+ t/s', 'vram': '~3.5 GB', 'best_for': 'Transparent, highly documented benchmarking.'},
    "smollm2-1.3b": {'model': 'HuggingFaceTB/SmolLM2-1.3B-Instruct', 'engine': 'transformers', 'type': 'fast', 'size': '1.3B', 'context': '8k', 'speed': '~100+ t/s', 'vram': '~3.5 GB', 'best_for': 'Tagging, filtering, and structuring web-scraped data.'},
    "granite-3-2b": {'model': 'ibm-granite/granite-3.0-2b-instruct', 'engine': 'transformers', 'type': 'fast', 'size': '2B', 'context': '4k', 'speed': '~80+ t/s', 'vram': '~5 GB', 'best_for': 'Enterprise-grade strict adherence and JSON output.'},
    "starcoder2-3b": {'model': 'bigcode/starcoder2-3b', 'engine': 'transformers', 'type': 'fast', 'size': '3B', 'context': '16k', 'speed': '~60+ t/s', 'vram': '~6.5 GB', 'best_for': 'The fastest specialized coding and autocomplete model.'},
    "stablelm-3b": {'model': 'stabilityai/stablelm-zephyr-3b', 'engine': 'transformers', 'type': 'fast', 'size': '3B', 'context': '4k', 'speed': '~60+ t/s', 'vram': '~6.5 GB', 'best_for': 'Snappy text generation and intermediate API bridging.'},
    "minicpm3-4b": {'model': 'openbmb/MiniCPM3-4B', 'engine': 'transformers', 'type': 'fast', 'size': '4B', 'context': '32k', 'speed': '~50+ t/s', 'vram': '~8 GB', 'best_for': 'Processing of technical logs and backend routing logic.'},
    "yi-1.5-6b": {'model': '01-ai/Yi-1.5-6B-Chat', 'engine': 'transformers', 'type': 'balanced', 'size': '6B', 'context': '4k', 'speed': '30-35 t/s', 'vram': '~7 GB (8-bit)', 'best_for': 'Dense codebase analysis and document extraction.'},
    "starcoder2-7b": {'model': 'bigcode/starcoder2-7b', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '16k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Repository-level context parsing and code generation.'},
    "mathstral-7b": {'model': 'mistralai/Mathstral-7B-v0.1', 'engine': 'transformers', 'type': 'balanced', 'size': '7.3B', 'context': '32k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Specialized mathematical theorems and proofs.'},
    "starling-7b": {'model': 'Nexusflow/Starling-LM-7B-beta', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '8k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Generating high-quality conversational training datasets.'},
    "olmo-7b": {'model': 'allenai/OLMo-7B-Instruct', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '2k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Fully transparent architecture for strict benchmarking.'},
    "hermes-3-8b": {'model': 'NousResearch/Hermes-3-Llama-3.1-8B', 'engine': 'transformers', 'type': 'balanced', 'size': '8B', 'context': '128k', 'speed': '25-30 t/s', 'vram': '~8.5 GB (8-bit)', 'best_for': 'Highly uncensored, deeply agentic roleplay and logic.'},
    "granite-3-8b": {'model': 'ibm-granite/granite-3.0-8b-instruct', 'engine': 'transformers', 'type': 'balanced', 'size': '8B', 'context': '4k', 'speed': '25-30 t/s', 'vram': '~8.5 GB (8-bit)', 'best_for': 'Strict JSON formatting and enterprise text pipelines.'},
    "aya-expanse-8b": {'model': 'CohereForAI/aya-expanse-8b', 'engine': 'transformers', 'type': 'balanced', 'size': '8B', 'context': '8k', 'speed': '25-30 t/s', 'vram': '~8.5 GB (8-bit)', 'best_for': 'Building diverse, highly multilingual instruction datasets.'},
    "minicpm-v-2.6": {'model': 'openbmb/MiniCPM-V-2_6', 'engine': 'transformers', 'type': 'balanced', 'size': '~8B', 'context': '32k', 'speed': '20-25 t/s', 'vram': '~8.5 GB (8-bit)', 'best_for': 'Incredible vision-language understanding on a budget.'},
    "yi-1.5-9b": {'model': '01-ai/Yi-1.5-9B-Chat', 'engine': 'transformers', 'type': 'balanced', 'size': '9B', 'context': '4k', 'speed': '20-25 t/s', 'vram': '~10 GB (8-bit)', 'best_for': 'Analyzing dense structural API information.'},
    "dolphin-2.8-mistral-7b-v02": {'model': 'cognitivecomputations/dolphin-2.8-mistral-7b-v02', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '32k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': 'Fast, uncensored and highly reliable variant based on Mistral.'},
    "dolphin-2.9-llama3-8b": {'model': 'cognitivecomputations/dolphin-2.9-llama3-8b', 'engine': 'transformers', 'type': 'balanced', 'size': '8B', 'context': '8k', 'speed': '25-30 t/s', 'vram': '~8.5 GB (8-bit)', 'best_for': 'Exceptionally smart uncensored model, great at writing scripts.'},
    "llama3.1-8b-abliterated": {'model': 'mlabonne/meta-llama-3.1-8B-Instruct-abliterated', 'engine': 'transformers', 'type': 'balanced', 'size': '8B', 'context': '128k', 'speed': '25-30 t/s', 'vram': '~8.5 GB (8-bit)', 'best_for': 'Official Llama 3.1 8B with refusal mechanism removed, preserving original intelligence.'},
    "gemma2-9b-abliterated-gguf": {'model': 'bartowski/gemma-2-9b-it-abliterated-GGUF', 'engine': 'llamacpp', 'type': 'balanced', 'size': '9B', 'context': '8k', 'speed': '20-25 t/s', 'vram': '~6.5 GB (4-bit)', 'best_for': 'Punches above its weight in logic and coding, abliterated for complex technical teardowns.'},

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
    },
    # 🎨 Predefined Image Generation Models
    "stable-diffusion-v1-5": {
        "model": "runwayml/stable-diffusion-v1-5",
        "engine": "diffusers",
        "task": "image",
        "type": "balanced",
        "size": "1B",
        "context": "N/A",
        "speed": "~2-4 s/img",
        "vram": "~4.5 GB",
        "best_for": "Fast and classic text-to-image synthesis."
    },
    "flux-schnell": {
        "model": "black-forest-labs/FLUX.1-schnell",
        "engine": "diffusers",
        "task": "image",
        "type": "large",
        "size": "12B",
        "context": "N/A",
        "speed": "~10-15 s/img",
        "vram": "~16 GB",
        "best_for": "State-of-the-art detail, realism, and prompt adherence."
    }
}

def load_dynamic_models():
    """
    Dynamically loads model catalog from remote CSV (GitHub raw CSV or custom URL).
    Falls back to static PREDEFINED_MODELS if request fails or offline.
    """
    import os
    import sys
    import urllib.request
    import csv
    import io
    import threading
    import time

    # Configure console encoding to avoid Windows UnicodeEncodeError on piped/redirected runs
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Check if a dynamic sync has already been performed in this process to avoid duplicate fetches
    if getattr(load_dynamic_models, "_synced", False):
        return

    sheet_url = os.getenv(
        "OPENRUN_MODELS_URL",
        os.getenv(
            "OPENRUN_MODELS_SHEET_URL",
            "https://raw.githubusercontent.com/devkiraa/OpenRun/main/openrun-models.csv"
        )
    )

    if not sheet_url:
        return

    is_tty = sys.stdout.isatty()

    class Spinner:
        def __init__(self):
            # A gorgeous, large symmetric organic breathing block wave gradient animation with absolutely no text!
            self.frames = []
            width = 41 # expanded width for a larger visual visualizer
            center = width // 2
            
            # Active blocks expanding from center: 1, 3, 5, ..., 41
            expansion_levels = list(range(1, width + 1, 2))
            
            # Forward expansion (breathing out)
            for active_count in expansion_levels:
                bar = ["▱"] * width
                half = active_count // 2
                for i in range(center - half, center + half + 1):
                    bar[i] = "▰"
                
                colored_bar = []
                for idx, char in enumerate(bar):
                    if char == "▰":
                        # Dynamic center-outward color gradient: Bright Emerald Green to Glowing Purple/Magenta
                        dist = abs(idx - center)
                        r = int(dist * 9)
                        g = int(255 - dist * 11)
                        b = int(130 + dist * 6)
                        r = max(0, min(255, r))
                        g = max(0, min(255, g))
                        b = max(0, min(255, b))
                        colored_bar.append(f"\033[38;2;{r};{g};{b}m{char}\033[0m")
                    else:
                        colored_bar.append(f"\033[90m{char}\033[0m")
                self.frames.append("".join(colored_bar))
                
            # Reverse contraction (breathing in)
            for active_count in reversed(expansion_levels[1:-1]):
                bar = ["▱"] * width
                half = active_count // 2
                for i in range(center - half, center + half + 1):
                    bar[i] = "▰"
                
                colored_bar = []
                for idx, char in enumerate(bar):
                    if char == "▰":
                        dist = abs(idx - center)
                        r = int(dist * 9)
                        g = int(255 - dist * 11)
                        b = int(130 + dist * 6)
                        r = max(0, min(255, r))
                        g = max(0, min(255, g))
                        b = max(0, min(255, b))
                        colored_bar.append(f"\033[38;2;{r};{g};{b}m{char}\033[0m")
                    else:
                        colored_bar.append(f"\033[90m{char}\033[0m")
                self.frames.append("".join(colored_bar))

            self.running = False
            self.thread = None

        def spin(self):
            idx = 0
            while self.running:
                sys.stdout.write(f"\r{self.frames[idx]}")
                sys.stdout.flush()
                time.sleep(0.05) # smooth breathing pulse frame rate
                idx = (idx + 1) % len(self.frames)

        def start(self):
            if not is_tty:
                return
            self.running = True
            self.thread = threading.Thread(target=self.spin, daemon=True)
            self.thread.start()

        def stop(self, success=True):
            if not is_tty:
                return
            self.running = False
            if self.thread:
                self.thread.join()
            sys.stdout.write("\r\033[K")  # Clear the line completely
            sys.stdout.flush()

    spinner = Spinner()
    spinner.start()

    success = False
    try:
        req = urllib.request.Request(
            sheet_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=3.0) as response:
            csv_data = response.read().decode('utf-8')

        f = io.StringIO(csv_data)
        reader = csv.DictReader(f)

        fetched_models = {}
        for row in reader:
            key = row.get("key") or row.get("model_key") or row.get("id") or row.get("Key") or row.get("Model Key")
            if not key:
                continue

            key = key.strip().lower()
            def _get_val(keys, default="N/A"):
                for k in keys:
                    v = row.get(k)
                    if v is not None and v.strip():
                        return v.strip()
                return default

            task_raw = _get_val(["task", "Task", "category", "Category"], "text").lower()
            if "image" in task_raw or "diff" in task_raw:
                task = "image"
            elif "embed" in task_raw:
                task = "embedding"
            else:
                task = "text"

            model_info = {
                "model": _get_val(["model", "Model"], ""),
                "engine": _get_val(["engine", "Engine"], "transformers"),
                "task": task,
                "type": _get_val(["type", "Type"], "balanced"),
                "size": _get_val(["size", "Size"]),
                "context": _get_val(["context", "Context"]),
                "speed": _get_val(["speed", "Speed"]),
                "vram": _get_val(["vram", "VRAM"]),
                "provider": _get_val(["provider", "Provider"], "Other"),
                "family": _get_val(["family", "Family"], "Other"),
                "best_for": _get_val(["best_for", "best_used_for", "Best Used For / Capabilities"])
            }
            if model_info["model"]:
                fetched_models[key] = model_info

        if fetched_models:
            global PREDEFINED_MODELS
            # Update dynamic dict safely without wiping out local image or embedding models
            PREDEFINED_MODELS.update(fetched_models)
            success = True
            load_dynamic_models._synced = True
    except Exception:
        success = False
    finally:
        spinner.stop(success)

# Ensure all static models have default task, provider, and family attributes if not specified
for key, info in PREDEFINED_MODELS.items():
    if "task" not in info:
        info["task"] = "text"
        
    # Infer provider if not specified
    if "provider" not in info:
        model_path = info.get("model", "").lower()
        key_lower = key.lower()
        if "deepseek" in key_lower or "deepseek" in model_path:
            info["provider"] = "DeepSeek"
        elif "llama" in key_lower or "meta" in model_path:
            if "abliterated" in key_lower or "abliterated" in model_path:
                info["provider"] = "Meta (Abliterated)"
            else:
                info["provider"] = "Meta"
        elif "qwen" in key_lower or "qwen" in model_path:
            info["provider"] = "Alibaba"
        elif "gemma" in key_lower or "google" in model_path:
            if "abliterated" in key_lower or "abliterated" in model_path:
                info["provider"] = "Google (Abliterated)"
            else:
                info["provider"] = "Google"
        elif "phi" in key_lower or "microsoft" in model_path:
            info["provider"] = "Microsoft"
        elif "mistral" in key_lower or "mathstral" in key_lower or "mistral" in model_path:
            info["provider"] = "Mistral"
        elif "smollm" in key_lower or "huggingface" in model_path:
            info["provider"] = "Hugging Face"
        elif "granite" in key_lower or "ibm" in model_path:
            info["provider"] = "IBM"
        elif "starcoder" in key_lower or "bigcode" in model_path:
            info["provider"] = "BigCode"
        elif "yi" in key_lower or "01-ai" in model_path:
            info["provider"] = "01.AI"
        elif "hermes" in key_lower or "nousresearch" in model_path:
            info["provider"] = "Nous Research"
        elif "aya" in key_lower or "cohere" in model_path:
            info["provider"] = "Cohere"
        elif "minicpm" in key_lower or "openbmb" in model_path:
            info["provider"] = "OpenBMB"
        elif "starling" in key_lower or "nexusflow" in model_path:
            info["provider"] = "Nexusflow"
        elif "stable-diffusion" in key_lower or "stability" in model_path:
            info["provider"] = "Stability AI"
        elif "flux" in key_lower or "black-forest-labs" in model_path:
            info["provider"] = "Black Forest Labs"
        elif "dolphin" in key_lower or "cognitivecomputations" in model_path:
            info["provider"] = "Cognitive Computations"
        elif "olmo" in key_lower or "allenai" in model_path:
            info["provider"] = "AllenAI"
        else:
            info["provider"] = "Other"

    # Infer family if not specified
    if "family" not in info:
        model_path = info.get("model", "").lower()
        key_lower = key.lower()
        if "deepseek-r1" in model_path or "distill" in model_path:
            info["family"] = "DeepSeek R1"
        elif "deepseek-coder" in key_lower or "deepseek-coder" in model_path:
            info["family"] = "DeepSeek Coder"
        elif "llama-3.2" in model_path or "llama3.2" in key_lower:
            info["family"] = "Llama 3.2"
        elif "llama-3.1" in model_path or "llama3.1" in key_lower:
            info["family"] = "Llama 3.1"
        elif "llama-3" in model_path or "llama3" in key_lower:
            info["family"] = "Llama 3"
        elif "qwen2.5-coder" in key_lower or "qwen2.5-coder" in model_path:
            info["family"] = "Qwen 2.5 Coder"
        elif "qwen2.5-math" in key_lower or "qwen2.5-math" in model_path:
            info["family"] = "Qwen 2.5 Math"
        elif "qwen2.5-vl" in key_lower or "qwen2.5-vl" in model_path:
            info["family"] = "Qwen 2.5 VL"
        elif "qwen2.5-omni" in key_lower or "qwen2.5-omni" in model_path:
            info["family"] = "Qwen 2.5 Omni"
        elif "qwen2.5" in key_lower or "qwen2.5" in model_path:
            info["family"] = "Qwen 2.5"
        elif "gemma-4" in key_lower or "gemma-4" in model_path:
            info["family"] = "Gemma 4"
        elif "gemma-2" in model_path or "gemma2" in key_lower:
            info["family"] = "Gemma 2"
        elif "codegemma" in key_lower or "codegemma" in model_path:
            info["family"] = "CodeGemma"
        elif "gemma" in key_lower or "gemma" in model_path:
            info["family"] = "Gemma"
        elif "phi-3.5" in model_path or "phi3.5" in key_lower:
            info["family"] = "Phi 3.5"
        elif "phi-4" in model_path or "phi4" in key_lower:
            info["family"] = "Phi 4"
        elif "phi-3" in model_path or "phi" in key_lower:
            info["family"] = "Phi 3"
        elif "mistral-nemo" in key_lower or "mistral-nemo" in model_path:
            info["family"] = "Mistral Nemo"
        elif "mistral" in key_lower or "mistral" in model_path:
            info["family"] = "Mistral"
        elif "mathstral" in key_lower or "mathstral" in model_path:
            info["family"] = "Mathstral"
        elif "smollm2" in key_lower or "smollm2" in model_path:
            info["family"] = "SmolLM2"
        elif "granite-3.0" in model_path or "granite" in key_lower:
            info["family"] = "Granite 3"
        elif "starcoder2" in key_lower or "starcoder2" in model_path:
            info["family"] = "StarCoder 2"
        elif "yi-1.5" in model_path or "yi" in key_lower:
            info["family"] = "Yi 1.5"
        elif "hermes" in key_lower or "hermes" in model_path:
            info["family"] = "Hermes"
        elif "aya" in key_lower or "aya" in model_path:
            info["family"] = "Aya"
        elif "minicpm" in key_lower or "minicpm" in model_path:
            info["family"] = "MiniCPM"
        elif "starling" in key_lower or "starling" in model_path:
            info["family"] = "Starling"
        elif "stable-diffusion" in key_lower or "stable-diffusion" in model_path:
            info["family"] = "Stable Diffusion"
        elif "flux" in key_lower or "flux" in model_path:
            info["family"] = "Flux"
        elif "dolphin" in key_lower or "dolphin" in model_path:
            info["family"] = "Dolphin"
        elif "olmo" in key_lower or "olmo" in model_path:
            info["family"] = "OLMo"
        else:
            info["family"] = "Other"