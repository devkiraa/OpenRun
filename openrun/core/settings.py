import os
import json

SETTINGS_DIR = os.path.expanduser("~/.openrun")
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")

def get_settings():
    if not os.path.exists(SETTINGS_DIR):
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        try:
            os.chmod(SETTINGS_DIR, 0o700)
        except Exception:
            pass
    if not os.path.exists(SETTINGS_FILE):
        default = {
            "cache_dir": os.path.expanduser("~/.cache/huggingface/hub"),
            "configured": False
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default, f, indent=4)
        try:
            os.chmod(SETTINGS_FILE, 0o600)
        except Exception:
            pass
        return default
    try:
        try:
            os.chmod(SETTINGS_FILE, 0o600)
        except Exception:
            pass
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "cache_dir": os.path.expanduser("~/.cache/huggingface/hub"),
            "configured": False
        }

def save_settings(settings):
    if not os.path.exists(SETTINGS_DIR):
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        try:
            os.chmod(SETTINGS_DIR, 0o700)
        except Exception:
            pass
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
    try:
        os.chmod(SETTINGS_FILE, 0o600)
    except Exception:
        pass

def get_cache_dir(interactive=True):
    """
    Returns the configured cache directory path.
    If interactive is True and settings have not been configured yet, prompts the user.
    """
    settings = get_settings()
    cache_dir = settings.get("cache_dir")
    
    if interactive and not settings.get("configured", False):
        import sys
        is_notebook = "google.colab" in sys.modules or "COLAB_GPU" in os.environ or "ipykernel" in sys.modules
        if sys.stdout.isatty() and sys.stdin.isatty() and not is_notebook:
            # Dynamically import questionary to avoid import overhead if not needed
            try:
                import questionary
                print("\n\033[1;93m📦 Model Storage Configuration\033[0m")
                print("To prevent redownloading weights, OpenRun can store models in a custom local directory.")
                
                path = questionary.text(
                    "Enter the local path to save downloaded models (or press Enter for default):",
                    default=cache_dir
                ).ask()
                
                if path:
                    cleaned_path = os.path.abspath(os.path.expanduser(path.strip()))
                    os.makedirs(cleaned_path, exist_ok=True)
                    settings["cache_dir"] = cleaned_path
                
                settings["configured"] = True
                save_settings(settings)
                cache_dir = settings["cache_dir"]
                print(f"\033[92m✔ Model storage path configured: {cache_dir}\033[0m\n")
            except Exception:
                pass
            
    return cache_dir
