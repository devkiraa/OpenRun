import subprocess
import threading
import shutil
import re

def _monitor_tunnel(process):
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    found = False
    
    for line in process.stdout:
        match = url_pattern.search(line)
        if match and not found:
            print(f"\n🌍 Public URL: {match.group(0)}\n")
            found = True
            # We found the URL, but we should continue reading the stream 
            # to prevent the pipe buffer from filling up and blocking the process.

    if not found:
        print("⚠️ Could not detect public URL automatically. Check logs above.")
        
def start_tunnel(port: int):
    """Starts a Cloudflare tunnel in the background pointing to the local port."""
    if not shutil.which("cloudflared"):
        print("\n⚠️  Error: 'cloudflared' is not installed or not in PATH.")
        print("To use --public, please install cloudflared:")
        print("  - Mac: brew install cloudflare/cloudflare/cloudflared")
        print("  - Linux: wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && dpkg -i cloudflared-linux-amd64.deb")
        print("  - Windows: winget install cloudflared")
        print("Or visit: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/\n")
        return

    print("🌐 Starting Cloudflare tunnel...")
    
    try:
        # cloudflared logs everything to stderr, so we merge it into stdout
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
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
