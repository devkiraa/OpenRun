import os
import sys
from openrun.models.registry import PREDEFINED_MODELS

def list_models():
    """
    Prints a clean, flat terminal table listing all predefined models and their specifications.
    """
    # Configure console encoding
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("\n\033[92m📦 OpenRun Predefined Models Registry\033[0m")
    print("\033[90m====================================================================================================================================\033[0m")

    # Table Header
    header = f"{'Model Key'.ljust(22)} │ {'Size'.rjust(6)} │ {'Speed'.rjust(11)} │ {'VRAM (4-bit)'.rjust(12)} │ {'Engine'.ljust(12)} │ {'Best Used For / Capabilities'}"
    print(f"\033[1;4m{header}\033[0m")

    # Filter out duplicate backward-compatibility aliases to keep the list clean
    aliases = {
        "qwen": "qwen3-8b",
        "deepseek": "deepseek-r1-8b",
        "phi": "phi-4-mini",
        "mistral": "mistral-nemo",
        "llama3": "llama3-8b",
        "llama70b": "llama3-70b",
        "gemma2:2b": "gemma2-2b"
    }

    for key, info in PREDEFINED_MODELS.items():
        if key in aliases:
            continue

        size = info.get("size", "N/A")
        speed = info.get("speed", "N/A")
        vram = info.get("vram", "N/A")
        engine = info.get("engine", "transformers")
        best_for = info.get("best_for", "N/A")

        # Color and highlight formatting
        f_key = f"\033[92m{key.ljust(22)}\033[0m"
        f_size = size.rjust(6)
        f_speed = f"\033[95m{speed.rjust(11)}\033[0m"
        f_vram = f"\033[93m{vram.rjust(12)}\033[0m"
        f_engine = f"\033[96m{engine.ljust(12)}\033[0m"
        f_best_for = f"\033[97m{best_for}\033[0m"

        print(f"{f_key} │ {f_size} │ {f_speed} │ {f_vram} │ {f_engine} │ {f_best_for}")

    print("\033[90m====================================================================================================================================\033[0m")
    print("\033[1m💡 To run a model, execute:\033[0m")
    print("   \033[94mopenrun run <model-key>\033[0m  (or  \033[94mpython -m openrun run <model-key>\033[0m)\n")
