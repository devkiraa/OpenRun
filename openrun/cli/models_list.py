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

    # Gather rows and calculate dynamic column widths
    rows = []
    max_key_len = len("Model Key")
    max_size_len = len("Size")
    max_speed_len = len("Speed")
    max_vram_len = len("VRAM (4-bit)")
    max_engine_len = len("Engine")

    for key, info in PREDEFINED_MODELS.items():
        if key in aliases:
            continue

        size = info.get("size", "N/A")
        speed = info.get("speed", "N/A")
        vram = info.get("vram", "N/A")
        engine = info.get("engine", "transformers")
        best_for = info.get("best_for", "N/A")

        rows.append((key, size, speed, vram, engine, best_for))

        max_key_len = max(max_key_len, len(key))
        max_size_len = max(max_size_len, len(size))
        max_speed_len = max(max_speed_len, len(speed))
        max_vram_len = max(max_vram_len, len(vram))
        max_engine_len = max(max_engine_len, len(engine))

    # Add spacing buffers (ensures at least 2 spaces gap between columns)
    w_key = max_key_len + 2
    w_size = max_size_len + 2
    w_speed = max_speed_len + 2
    w_vram = max_vram_len + 2
    w_engine = max_engine_len + 2

    # Draw top border
    border_len = w_key + w_size + w_speed + w_vram + w_engine + 16 + 65
    print("\033[90m" + "─" * border_len + "\033[0m")

    # Table Header
    header = f"{'Model Key'.ljust(w_key)} │ {'Size'.rjust(w_size)} │ {'Speed'.rjust(w_speed)} │ {'VRAM (4-bit)'.rjust(w_vram)} │ {'Engine'.ljust(w_engine)} │ {'Best Used For / Capabilities'}"
    print(f"\033[1;4m{header}\033[0m")

    # Print rows with perfect alignments
    for key, size, speed, vram, engine, best_for in rows:
        f_key = f"\033[92m{key.ljust(w_key)}\033[0m"
        f_size = size.rjust(w_size)
        f_speed = f"\033[95m{speed.rjust(w_speed)}\033[0m"
        f_vram = f"\033[93m{vram.rjust(w_vram)}\033[0m"
        f_engine = f"\033[96m{engine.ljust(w_engine)}\033[0m"
        f_best_for = f"\033[97m{best_for}\033[0m"

        print(f"{f_key} │ {f_size} │ {f_speed} │ {f_vram} │ {f_engine} │ {f_best_for}")

    # Draw bottom border
    print("\033[90m" + "─" * border_len + "\033[0m")
    print("\033[1m💡 To run a model, execute:\033[0m")
    print("   \033[94mopenrun run <model-key>\033[0m  (or  \033[94mpython -m openrun run <model-key>\033[0m)\n")
