import threading
import inspect
import uvicorn
import secrets
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

def serve(fn, public=False, api_key=None, port=8000):
    if api_key is None:
        api_key = "sk-or-" + secrets.token_hex(8)
        
    print("🚀 OpenRun running")
    print(f"🔐 API Key: {api_key}")
    
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

    if public:
        import time
        time.sleep(1)
        start_tunnel(port)
    else:
        print(f"🌍 URL: http://localhost:{port}")
        
    print("📡 Endpoint: /v1/chat/completions")
    
    print("\n📡 Example Request:\n")
    print(f"""curl -X POST http://localhost:{port}/v1/chat/completions \\
-H "Authorization: Bearer {api_key}" \\
-H "Content-Type: application/json" \\
-d '{{"messages":[{{"role":"user","content":"Hello"}}]}}'
""")
