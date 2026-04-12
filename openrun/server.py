import threading
import inspect
import uvicorn
import secrets
import time
import socket
import string
from openrun.core.state import set_global_state, get_global_state
from openrun.core.config import Config
from openrun.network.server import create_app
from openrun.network.tunnel import start_tunnel
from openrun.adapters.base import BaseAdapter

class InlineAdapter(BaseAdapter):
    def __init__(self, fn):
        self.fn = fn
        self.func_type = "prompt"
        
        try:
            sig = inspect.signature(fn)
            if "messages" in sig.parameters:
                self.func_type = "messages"
        except:
            if getattr(fn, "__name__", "") == "chat":
                self.func_type = "messages"

    def load(self):
        pass

    def generate(self, input_data: list) -> str:
        if self.func_type == "messages":
            return self.fn(input_data)
        else:
            prompt = input_data[-1]["content"] if input_data else ""
            return self.fn(prompt)

    def stream(self, input_data: list):
        response = self.generate(input_data)
        for word in response.split():
            yield word + " "

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def serve(fn, public=False, api_key=None, port=None):
    if port is None:
        port = get_free_port()
    elif is_port_in_use(port):
        print(f"⚠️ Port {port} busy. Switching automatically...")
        port = get_free_port()

    if api_key is None:
        api_key = "sk-or-" + secrets.token_hex(8)
        
    config = Config(
        model="inline-model",
        file=None,
        port=port,
        public=public,
        api_key=api_key
    )
    
    adapter = InlineAdapter(fn)
    adapter.load()
    
    set_global_state(config=config, model=None, adapter=adapter)
    
    app = create_app()
    
    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    # Start server in background thread for non-blocking mode
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    def wait_for_server(port, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("localhost", port)) == 0:
                    return True
            time.sleep(0.2)
        return False

    if not wait_for_server(port):
        print("❌ Server failed to start.")
        return

    print("🚀 OpenRun running")
    print(f"🔐 API Key: {api_key}")

    if public:
        start_tunnel(port)
    else:
        print(f"🌍 URL: http://localhost:{port}")
        
    print("📡 Endpoint: /v1/chat/completions")
    print("❤️ Health: /health")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 OpenRun stopped")
