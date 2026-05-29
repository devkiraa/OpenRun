import os
import sys
from openrun.models.registry import PREDEFINED_MODELS, load_dynamic_models

def list_models(search=None, task="all"):
    """
    Prints a clean, grouped terminal table listing predefined models and their specifications.
    Supports filtering by search query and task type.
    """
    # Try fetching latest models catalog dynamically from Google Sheets
    try:
        load_dynamic_models()
    except Exception:
        pass

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

    # Gather rows by task category and calculate overall dynamic column widths
    groups = {
        "text": [],
        "image": [],
        "embedding": [],
        "other": []
    }
    
    max_key_len = len("Model Key")
    max_size_len = len("Size")
    max_speed_len = len("Speed")
    max_vram_len = len("VRAM (4-bit)")
    max_engine_len = len("Engine")

    query = search.strip().lower() if search else None

    for key, info in PREDEFINED_MODELS.items():
        if key in aliases:
            continue

        model_name = info.get("model", "")
        best_for = info.get("best_for", "N/A")
        
        # 1. Search Query Filter
        if query:
            match = (
                query in key.lower() or 
                query in model_name.lower() or 
                query in best_for.lower()
            )
            if not match:
                continue

        # 2. Task Filter
        model_task = info.get("task", "text").lower()
        if task != "all" and model_task != task:
            continue

        size = info.get("size", "N/A")
        speed = info.get("speed", "N/A")
        vram = info.get("vram", "N/A")
        engine = info.get("engine", "transformers")

        row = (key, size, speed, vram, engine, best_for)
        
        # Group assignment
        if model_task in groups:
            groups[model_task].append(row)
        else:
            groups["other"].append(row)

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

    import textwrap

    try:
        terminal_columns = os.get_terminal_size().columns
    except Exception:
        terminal_columns = 120

    w_sno = 5
    left_col_width = w_sno + 3 + w_key + 3 + w_size + 3 + w_speed + 3 + w_vram + 3 + w_engine
    left_width = left_col_width + 3 # including the final ' │ '
    desc_width = max(30, terminal_columns - left_width - 2)

    # Task header display configurations
    task_headers = {
        "text": "🌐 TEXT GENERATION MODELS",
        "image": "🎨 IMAGE GENERATION MODELS",
        "embedding": "🧠 EMBEDDING & VECTOR MODELS",
        "other": "📦 OTHER UTILITY MODELS"
    }

    total_printed = 0
    border_len = left_width + desc_width
    s_no = 1

    for task_name, rows in groups.items():
        if not rows:
            continue

        total_printed += len(rows)
        # Category Group Header
        print(f"\n\033[1;93m{task_headers[task_name]}\033[0m")
        print("\033[90m" + "─" * border_len + "\033[0m")

        # Table Header
        header = f"{'S.No'.ljust(w_sno)} │ {'Model Key'.ljust(w_key)} │ {'Size'.rjust(w_size)} │ {'Speed'.rjust(w_speed)} │ {'VRAM (4-bit)'.rjust(w_vram)} │ {'Engine'.ljust(w_engine)} │ {'Best Used For / Capabilities'}"
        print(f"\033[1;4m{header}\033[0m")

        # Print rows
        for key, size, speed, vram, engine, best_for in rows:
            f_sno = f"{s_no}".ljust(w_sno)
            f_key = f"\033[92m{key.ljust(w_key)}\033[0m"
            f_size = size.rjust(w_size)
            f_speed = f"\033[95m{speed.rjust(w_speed)}\033[0m"
            f_vram = f"\033[93m{vram.rjust(w_vram)}\033[0m"
            f_engine = f"\033[96m{engine.ljust(w_engine)}\033[0m"

            desc_lines = textwrap.wrap(best_for, width=desc_width)
            if not desc_lines:
                desc_lines = ["N/A"]

            print(f"{f_sno} │ {f_key} │ {f_size} │ {f_speed} │ {f_vram} │ {f_engine} │ \033[97m{desc_lines[0]}\033[0m")
            
            indent = " " * left_col_width
            for extra_line in desc_lines[1:]:
                print(f"{indent} │ \033[97m{extra_line}\033[0m")
            
            s_no += 1
        
        print("\033[90m" + "─" * border_len + "\033[0m")

    if total_printed == 0:
        print("\033[91m❌ No models found matching your search filters.\033[0m")

    print("\033[1m💡 To run a model, execute:\033[0m")
    print("   \033[94mopenrun run <model-key>\033[0m  (or  \033[94mpython -m openrun run <model-key>\033[0m)\n")
