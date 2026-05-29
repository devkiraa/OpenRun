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
    "gemma2-2b": {'model': 'google/gemma-2-2b-it', 'engine': 'transformers', 'type': 'fast', 'size': '2.6B', 'context': '8k', 'speed': '~75+ t/s', 'vram': '~6 GB', 'best_for': "Google's dense architecture for logic puzzles."},
    "codegemma-7b": {'model': 'google/codegemma-7b-it', 'engine': 'transformers', 'type': 'balanced', 'size': '7B', 'context': '8k', 'speed': '25-30 t/s', 'vram': '~8 GB (8-bit)', 'best_for': "Google's specialized instruction-following code model."},
    "gemma2-9b": {'model': 'google/gemma-2-9b-it', 'engine': 'transformers', 'type': 'balanced', 'size': '9B', 'context': '8k', 'speed': '20-25 t/s', 'vram': '~10 GB (8-bit)', 'best_for': 'High-end general text tasks (hits above its weight class).'},

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
    Dynamically loads model catalog from Google Sheets (CSV format).
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
        "OPENRUN_MODELS_SHEET_URL",
        "https://docs.google.com/spreadsheets/d/12AF0ixg2X2LpapPReZwZdeh7mX-er4xm1NGIaZoNjLg/export?format=csv"
    )

    if not sheet_url:
        return

    is_tty = sys.stdout.isatty()

    class Spinner:
        def __init__(self, message="Syncing dynamic models catalog..."):
            self.spinner_chars = [
                "▰▱▱▱▱▱▱", 
                "▱▰▱▱▱▱▱", 
                "▱▱▰▱▱▱▱", 
                "▱▱▱▰▱▱▱", 
                "▱▱▱▱▰▱▱", 
                "▱▱▱▱▱▰▱", 
                "▱▱▱▱▱▱▰",
                "▱▱▱▱▱▰▱",
                "▱▱▱▱▰▱▱",
                "▱▱▱▰▱▱▱",
                "▱▱▰▱▱▱▱",
                "▱▰▱▱▱▱▱"
            ]
            self.message = message
            self.running = False
            self.thread = None

        def spin(self):
            idx = 0
            while self.running:
                sys.stdout.write(f"\r\033[96m{self.spinner_chars[idx]}\033[0m {self.message}")
                sys.stdout.flush()
                time.sleep(0.08)
                idx = (idx + 1) % len(self.spinner_chars)

        def start(self):
            if not is_tty:
                print(f"🔄 {self.message}")
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
            sys.stdout.write("\r\033[K")  # Clear the line
            sys.stdout.flush()
            if success:
                print("\033[92m✔ Dynamic models catalog successfully synced.\033[0m")
            else:
                print("\033[90mℹ Offline. Using standard offline models catalog.\033[0m")

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

# Ensure all static models have a default task of 'text' if not specified
for info in PREDEFINED_MODELS.values():
    if "task" not in info:
        info["task"] = "text"