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

    # Gather all filtered rows and calculate dynamic column widths
    all_rows = []
    
    max_key_len = len("Key")
    max_model_len = len("Model")
    max_engine_len = len("Engine")
    max_type_len = len("Type")
    max_size_len = len("Size")
    max_context_len = len("Context")
    max_speed_len = len("Speed")
    max_vram_len = len("VRAM")
    max_provider_len = len("Provider")
    max_family_len = len("Family")

    query = search.strip().lower() if search else None

    for key, info in PREDEFINED_MODELS.items():
        if key in aliases:
            continue

        model_name = info.get("model", "")
        best_for = info.get("best_for", "N/A")
        provider = info.get("provider", "Other")
        family = info.get("family", "Other")
        
        # 1. Search Query Filter
        if query:
            match = (
                query in key.lower() or 
                query in model_name.lower() or 
                query in provider.lower() or 
                query in family.lower() or 
                query in best_for.lower()
            )
            if not match:
                continue

        # 2. Task Filter
        model_task = info.get("task", "text").lower()
        if task != "all" and model_task != task:
            continue

        engine = info.get("engine", "transformers")
        type_val = info.get("type", "balanced")
        size = info.get("size", "N/A")
        context = info.get("context", "N/A")
        speed = info.get("speed", "N/A")
        vram = info.get("vram", "N/A")

        row = (key, model_name, engine, type_val, size, context, speed, vram, provider, family, best_for)
        all_rows.append(row)

        max_key_len = max(max_key_len, len(key))
        max_model_len = max(max_model_len, len(model_name))
        max_engine_len = max(max_engine_len, len(engine))
        max_type_len = max(max_type_len, len(type_val))
        max_size_len = max(max_size_len, len(size))
        max_context_len = max(max_context_len, len(context))
        max_speed_len = max(max_speed_len, len(speed))
        max_vram_len = max(max_vram_len, len(vram))
        max_provider_len = max(max_provider_len, len(provider))
        max_family_len = max(max_family_len, len(family))

    # Add spacing buffers (ensures at least 2 spaces gap between columns)
    w_key = max_key_len + 2
    w_model = max_model_len + 2
    w_engine = max_engine_len + 2
    w_type = max_type_len + 2
    w_size = max_size_len + 2
    w_context = max_context_len + 2
    w_speed = max_speed_len + 2
    w_vram = max_vram_len + 2
    w_provider = max_provider_len + 2
    w_family = max_family_len + 2

    import textwrap

    try:
        terminal_columns = os.get_terminal_size().columns
    except Exception:
        terminal_columns = 120

    w_sno = 5
    left_col_width = (
        w_sno + 3 + 
        w_key + 3 + 
        w_model + 3 + 
        w_engine + 3 + 
        w_type + 3 + 
        w_size + 3 + 
        w_context + 3 + 
        w_speed + 3 + 
        w_vram + 3 + 
        w_provider + 3 + 
        w_family
    )
    left_width = left_col_width + 3 # including the final ' │ '
    desc_width = max(30, terminal_columns - left_width - 2)

    total_printed = len(all_rows)
    border_len = left_width + desc_width
    s_no = 1

    # Helper to calculate sorting priority: Provider, Family, Size, Key
    def get_sort_key(row):
        provider = row[8]
        family = row[9]
        size_str = row[4].upper() if row[4] else ""
        params = 0.0
        try:
            if "M" in size_str:
                params = float(size_str.replace("M", "").split()[0]) / 1000.0
            elif "B" in size_str:
                params = float(size_str.replace("B", "").split()[0])
        except Exception:
            pass
            
        p_lower = provider.lower()
        p_sort = "zzz_" + p_lower if p_lower in ["other", "none", "n/a", ""] else p_lower
        
        f_lower = family.lower()
        f_sort = "zzz_" + f_lower if f_lower in ["other", "none", "n/a", ""] else f_lower
        
        return (p_sort, f_sort, params, row[0].lower())

    if all_rows:
        all_rows.sort(key=get_sort_key)

        print("\033[90m" + "─" * border_len + "\033[0m")

        # Table Header containing all CSV columns in order
        header = (
            f"{'S.No'.ljust(w_sno)} │ "
            f"{'Key'.ljust(w_key)} │ "
            f"{'Model'.ljust(w_model)} │ "
            f"{'Engine'.ljust(w_engine)} │ "
            f"{'Type'.ljust(w_type)} │ "
            f"{'Size'.rjust(w_size)} │ "
            f"{'Context'.rjust(w_context)} │ "
            f"{'Speed'.rjust(w_speed)} │ "
            f"{'VRAM'.rjust(w_vram)} │ "
            f"{'Provider'.ljust(w_provider)} │ "
            f"{'Family'.ljust(w_family)} │ "
            f"{'Best Used For / Capabilities'}"
        )
        print(f"\033[1;4m{header}\033[0m")

        # Print all models in a single table
        for key, model_name, engine, type_val, size, context, speed, vram, provider, family, best_for in all_rows:
            f_sno = f"{s_no}".ljust(w_sno)
            f_key = f"\033[92m{key.ljust(w_key)}\033[0m"
            f_model = f"\033[90m{model_name.ljust(w_model)}\033[0m"
            f_engine = f"\033[96m{engine.ljust(w_engine)}\033[0m"
            f_type = f"\033[38;2;165;100;0m{type_val.ljust(w_type)}\033[0m"
            f_size = size.rjust(w_size)
            f_context = context.rjust(w_context)
            f_speed = f"\033[95m{speed.rjust(w_speed)}\033[0m"
            f_vram = f"\033[93m{vram.rjust(w_vram)}\033[0m"
            f_provider = f"\033[38;2;210;170;15m{provider.ljust(w_provider)}\033[0m"
            f_family = f"\033[38;2;250;130;30m{family.ljust(w_family)}\033[0m"

            desc_lines = textwrap.wrap(str(best_for or "N/A"), width=desc_width)
            if not desc_lines:
                desc_lines = ["N/A"]

            print(
                f"{f_sno} │ {f_key} │ {f_model} │ {f_engine} │ {f_type} │ "
                f"{f_size} │ {f_context} │ {f_speed} │ {f_vram} │ "
                f"{f_provider} │ {f_family} │ \033[97m{desc_lines[0]}\033[0m"
            )
            
            indent = " " * left_col_width
            for extra_line in desc_lines[1:]:
                print(f"{indent} │ \033[97m{extra_line}\033[0m")
            
            s_no += 1
        
        print("\033[90m" + "─" * border_len + "\033[0m")

    if total_printed == 0:
        print("\033[91m❌ No models found matching your search filters.\033[0m")

    print("\033[1m💡 To run a model, execute:\033[0m")
    print("   \033[94mopenrun run <model-key>\033[0m  (or  \033[94mpython -m openrun run <model-key>\033[0m)\n")
