import os
import sys
from openrun.models.registry import PREDEFINED_MODELS

def list_models():
    """
    Prints a beautifully formatted, colorized terminal table listing all predefined models,
    grouped by engine, including VRAM usage, inference speeds, and best use cases.
    """
    # Configure console encoding
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("\n\033[92m📦 OpenRun Predefined Models Registry\033[0m")
    print("\033[90m========================================================================================================================\033[0m\n")

    # Group by engine
    grouped = {}
    for key, info in PREDEFINED_MODELS.items():
        # Avoid listing duplicate aliases to keep the table super clean
        aliases = {
            "qwen": "qwen3-8b",
            "deepseek": "deepseek-r1-8b",
            "phi": "phi-4-mini",
            "mistral": "mistral-nemo",
            "llama3": "llama3-8b",
            "llama70b": "llama3-70b",
            "gemma2:2b": "gemma2-2b"
        }
        if key in aliases:
            continue

        engine = info.get("engine", "transformers").capitalize()
        if engine not in grouped:
            grouped[engine] = []
        grouped[engine].append((key, info))

    for engine, models in grouped.items():
        # Select category emoji and color
        if engine.lower() == "transformers":
            header_color = "\033[96m"  # Cyan
            icon = "⚡"
        elif engine.lower() == "airllm":
            header_color = "\033[93m"  # Yellow
            icon = "🧠"
        else:
            header_color = "\033[95m"  # Magenta
            icon = "🦙"

        print(f"{icon} {header_color}\033[1m{engine} Engine Models\033[0m")
        print("\033[90m" + "─" * 120 + "\033[0m")

        # Table Header
        header = f"{'Model Key'.ljust(22)} │ {'Size'.rjust(6)} │ {'Speed'.rjust(11)} │ {'VRAM (4-bit)'.rjust(12)} │ {'Best Used For / Capabilities'}"
        print(f"\033[4m{header}\033[0m")

        for key, info in models:
            size = info.get("size", "N/A")
            speed = info.get("speed", "N/A")
            vram = info.get("vram", "N/A")
            best_for = info.get("best_for", "N/A")

            # Highlighting keys and columns
            f_key = f"\033[92m{key.ljust(22)}\033[0m"
            f_size = size.rjust(6)
            f_speed = f"\033[95m{speed.rjust(11)}\033[0m"
            f_vram = f"\033[93m{vram.rjust(12)}\033[0m"
            f_best_for = f"\033[97m{best_for}\033[0m"

            print(f"{f_key} │ {f_size} │ {f_speed} │ {f_vram} │ {f_best_for}")

        print("\033[90m" + "─" * 120 + "\033[0m")
        print("\033[1m💡 To run a model, execute:\033[0m")
        sample_key = models[0][0]
        print(f"   \033[94mopenrun run {sample_key}\033[0m  (or  \033[94mpython -m openrun run {sample_key}\033[0m)\n")

    # Add a note about custom files
    print("\033[90m" + "=" * 120 + "\033[0m")
    print("🛠️  \033[1mWant to run a custom local Python model?\033[0m")
    print("   Provide your own file path: \033[94mopenrun serve --file path/to/model.py\033[0m\n")
