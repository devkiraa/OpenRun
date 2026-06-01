import subprocess
import threading
import shutil
import re
import platform

def ensure_cloudflared():
    if shutil.which("cloudflared"):
        return "cloudflared"

    system = platform.system().lower()

    print("⚡ cloudflared not found. Installing automatically...")

    if system == "linux":
        subprocess.run(
            "wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        subprocess.run("dpkg -i cloudflared-linux-amd64.deb", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "cloudflared"

    elif system == "darwin":
        subprocess.run("brew install cloudflare/cloudflare/cloudflared", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "cloudflared"

    elif system == "windows":
        print("⚠️ Auto install not supported on Windows.")
        print("👉 Run: winget install cloudflared")
        return None

    else:
        print("⚠️ Unsupported OS for auto-install.")
        return None

def _monitor_tunnel(process):
    from openrun.core.state import global_state
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    found = False
    
    while True:
        line = process.stdout.readline()
        if not line:
            break
        match = url_pattern.search(line)
        if match and not found:
            url = match.group(0)
            api_base_url = f"{url}/v1"
            api_endpoint = f"{url}/v1/chat/completions"
            docs_url = f"{url}/docs"
            
            # Fetch model name
            model_name = "openrun"
            if global_state:
                if global_state.adapter and hasattr(global_state.adapter, 'model_name'):
                    model_name = global_state.adapter.model_name
                elif global_state.config and global_state.config.model:
                    model_name = global_state.config.model

            api_key = getattr(global_state.config, 'api_key', None) if global_state.config else None
            
            # Construct Hosted Web Chat Share Link
            from urllib.parse import quote
            base_chat_domain = "https://openrun-web.vercel.app/"
            params = f"?url={quote(api_base_url)}&theme=dark"
            if model_name:
                params += f"&model={quote(model_name)}"
            share_url = base_chat_domain + params
            
            # OSC 8 Clickable Link
            click_text = "Click to Open Web Chat"
            osc8_link = f"\033]8;;{share_url}\033\\{click_text}\033]8;;\033\\"
            
            # Theme colors (Sunset Ember / Amber Gold / Clean White)
            border = "\033[92m" # Emerald green for public tunnel box
            header = "\033[38;2;210;170;15m"
            key_color = "\033[38;2;250;130;30m"
            text = "\033[97m"
            dim = "\033[90m"
            link_color = "\033[38;2;30;144;255m"
            reset = "\033[0m"
            
            # Calculate box width dynamically to prevent wrapping
            box_width = max(60, len(api_endpoint) + 18)
            
            title_text = "  OPENRUN PUBLIC CLOUD TUNNEL IS LIVE & SECURE"
            endpoint_label = "  • Public API:   "
            docs_label = "  • Swagger UI:   "
            chat_label = "  • Web Chat UI:  "
            key_label = "  • API Key:      "
            
            title_row = title_text.ljust(box_width)
            endpoint_row = (endpoint_label + api_endpoint).ljust(box_width)
            docs_row = (docs_label + docs_url).ljust(box_width)
            
            if api_key:
                masked_key = api_key
                if len(api_key) > 20:
                    masked_key = api_key[:8] + "..." + api_key[-8:]
                key_value = masked_key
                key_color_code = key_color
            else:
                key_value = "None (Open Public Access)"
                key_color_code = dim

            key_plain_str = key_label + key_value
            key_padded = key_plain_str.ljust(box_width)
            val_start = key_padded.find(key_value)
            key_row = key_padded[:val_start] + key_color_code + key_value + reset + key_padded[val_start + len(key_value):]

            import sys
            import os
            is_notebook = "google.colab" in sys.modules or "COLAB_GPU" in os.environ or "ipykernel" in sys.modules

            if is_notebook:
                chat_value = "See Link Below"
                chat_plain_str = chat_label + f"[{chat_value}]"
                chat_padded = chat_plain_str.ljust(box_width)
                val_start = chat_padded.find(f"[{chat_value}]")
                chat_row = chat_padded[:val_start] + link_color + f"[{chat_value}]" + reset + chat_padded[val_start + len(f"[{chat_value}]"):]
            else:
                chat_plain_str = chat_label + f"[{click_text}]"
                chat_padded = chat_plain_str.ljust(box_width)
                val_start = chat_padded.find(f"[{click_text}]")
                chat_row = chat_padded[:val_start] + link_color + f"[{osc8_link}]" + reset + chat_padded[val_start + len(f"[{click_text}]"):]

            # Draw green box
            print(f"\n{border}┌" + "─"*box_width + f"┐{reset}")
            print(f"{border}│{reset}{header}{title_row}{reset}{border}│{reset}")
            print(f"{border}├" + "─"*box_width + f"┤{reset}")
            print(f"{border}│{reset}{text}{endpoint_row}{reset}{border}│{reset}")
            print(f"{border}│{reset}{text}{docs_row}{reset}{border}│{reset}")
            print(f"{border}│{reset}{text}{chat_row}{reset}{border}│{reset}")
            print(f"{border}│{reset}{text}{key_row}{reset}{border}│{reset}")
            print(f"{border}└" + "─"*box_width + f"┘{reset}")
            
            # Print the raw link right below so they can copy it with one click
            print(f"👉 {text}Share / Copy Web Chat Link:{reset} {link_color}{share_url}{reset}\n")
            found = True
            # We found the URL, but we should continue reading the stream 
            # to prevent the pipe buffer from filling up and blocking the process.

    if not found:
        print("⚠️ Could not detect public URL automatically. Check logs above.")
        
def start_tunnel(port: int):
    """Starts a Cloudflare tunnel in the background pointing to the local port."""
    binary = ensure_cloudflared()
    if not binary:
        return

    print("🌐 Starting Cloudflare tunnel...")
    
    try:
        # cloudflared logs everything to stderr, so we merge it into stdout
        process = subprocess.Popen(
            [binary, "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor the output in a separate daemon thread so it doesn't block
        thread = threading.Thread(target=_monitor_tunnel, args=(process,), daemon=True)
        thread.start()
        
    except Exception as e:
        print(f"\n⚠️  Failed to start Cloudflare tunnel: {e}\n")
