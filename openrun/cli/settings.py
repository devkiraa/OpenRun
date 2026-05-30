import sys
import os
from openrun.core.settings import get_settings, save_settings

def run_settings_menu():
    """
    Launches the settings configurator menu.
    Uses interactive arrow-key lists in a normal TTY terminal, and plain text listings in other environments.
    """
    # Configure console encoding
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    settings = get_settings()
    cache_dir = settings.get("cache_dir", os.path.expanduser("~/.cache/huggingface/hub"))
    default_port = settings.get("default_port", 8000)
    default_api_key = settings.get("api_key")
    default_api_key_str = f"\"{default_api_key}\"" if default_api_key else "None (Public Access)"

    hf_token = settings.get("hf_token")
    hf_token_str = "None"
    if hf_token:
        if len(hf_token) > 8:
            hf_token_str = f"\"{hf_token[:8]}...\""
        else:
            hf_token_str = "\"*****\""

    print("\n\033[1;93m⚙️  OpenRun Configuration Settings Manager\033[0m")
    
    is_notebook = "google.colab" in sys.modules or "COLAB_GPU" in os.environ or "ipykernel" in sys.modules
    is_interactive = sys.stdout.isatty() and sys.stdin.isatty() and not is_notebook
    
    if is_interactive:
        try:
            import questionary
            
            while True:
                choice = questionary.select(
                    "Select a configuration option to adjust:",
                    choices=[
                        f"📦 Model Cache Directory (Current: {cache_dir})",
                        f"🔌 Default Server Port   (Current: {default_port})",
                        f"🔑 Default API Key       (Current: {default_api_key_str})",
                        f"🤗 Hugging Face Token    (Current: {hf_token_str})",
                        "↩ Exit Configuration"
                    ]
                ).ask()
                
                if not choice or "Exit" in choice:
                    print("\033[90mConfiguration changes saved cleanly.\033[0m\n")
                    break
                    
                if "Model Cache Directory" in choice:
                    new_path = questionary.text(
                        "Enter the new local directory for downloading models:",
                        default=cache_dir
                    ).ask()
                    if new_path is not None:
                        cleaned_path = os.path.abspath(os.path.expanduser(new_path.strip()))
                        os.makedirs(cleaned_path, exist_ok=True)
                        settings["cache_dir"] = cleaned_path
                        settings["configured"] = True
                        save_settings(settings)
                        cache_dir = cleaned_path
                        print(f"\033[92m✔ Cache directory updated to: {cleaned_path}\033[0m\n")
                        
                elif "Default Server Port" in choice:
                    new_port = questionary.text(
                        "Enter the default port for OpenRun servers:",
                        default=str(default_port)
                    ).ask()
                    if new_port is not None:
                        try:
                            port_int = int(new_port.strip())
                            settings["default_port"] = port_int
                            save_settings(settings)
                            default_port = port_int
                            print(f"\033[92m✔ Default server port updated to: {port_int}\033[0m\n")
                        except ValueError:
                            print("\033[91m⚠️ Invalid port number. Must be an integer.\033[0m\n")
                            
                elif "Default API Key" in choice:
                    new_key = questionary.text(
                        "Enter the default server API Key (or enter 'None' to clear):",
                        default=default_api_key if default_api_key else ""
                    ).ask()
                    if new_key is not None:
                        key_val = new_key.strip()
                        if key_val.lower() == "none" or key_val == "":
                            settings["api_key"] = None
                            default_api_key = None
                            default_api_key_str = "None (Public Access)"
                        else:
                            settings["api_key"] = key_val
                            default_api_key = key_val
                            default_api_key_str = f"\"{key_val}\""
                        save_settings(settings)
                        print(f"\033[92m✔ Default API key updated to: {default_api_key_str}\033[0m\n")
                        
                elif "Hugging Face Token" in choice:
                    new_token = questionary.text(
                        "Enter your Hugging Face API Token (or enter 'None' to clear):",
                        default=hf_token if hf_token else ""
                    ).ask()
                    if new_token is not None:
                        token_val = new_token.strip()
                        if token_val.lower() == "none" or token_val == "":
                            settings["hf_token"] = None
                            hf_token = None
                            hf_token_str = "None"
                        else:
                            settings["hf_token"] = token_val
                            hf_token = token_val
                            if len(token_val) > 8:
                                hf_token_str = f"\"{token_val[:8]}...\""
                            else:
                                hf_token_str = "\"*****\""
                        save_settings(settings)
                        print(f"\033[92m✔ Hugging Face Token updated to: {hf_token_str}\033[0m\n")
        except Exception as e:
            # Fallback to plain print on errors
            is_interactive = False
            
    if not is_interactive:
        # Non-interactive / other way (simple console list / read)
        print(f"\033[90m[INFO] Non-interactive stream detected. Showing active parameters:\033[0m")
        print(f"  • \033[1mModel Cache Directory:\033[0m {cache_dir}")
        print(f"  • \033[1mDefault Server Port:\033[0m   {default_port}")
        print(f"  • \033[1mDefault API Key:\033[0m       {default_api_key_str}")
        print(f"  • \033[1mHugging Face Token:\033[0m    {hf_token_str}\n")
