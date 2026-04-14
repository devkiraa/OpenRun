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
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    found = False
    
    for line in process.stdout:
        match = url_pattern.search(line)
        if match and not found:
            url = match.group(0)
            print("\n\033[92m" + "╭" + "─"*55 + "╮\033[0m")
            print(f"\033[92m│\033[0m 🌍 \033[1mPublic URL:\033[0m \033[96m{url.ljust(39)}\033[0m \033[92m│\033[0m")
            print("\033[92m" + "╰" + "─"*55 + "╯\033[0m\n")
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
