import uvicorn
import time
import os
from huggingface_hub import login
from openrun.core.config import Config
from openrun.core.state import set_global_state, get_global_state
from openrun.network.server import create_app
from openrun.network.tunnel import start_tunnel
from openrun.models.registry import PREDEFINED_MODELS
from openrun.adapters.huggingface import HuggingFaceAdapter
from openrun.adapters.airllm import AirLLMAdapter

def run_predefined(args):
    model_key = args.model_name.lower()
    
    if model_key not in PREDEFINED_MODELS:
        print(f"❌ Error: Predefined model '{model_key}' not found.")
        print(f"Available models: {', '.join(PREDEFINED_MODELS.keys())}")
        return

    model_info = PREDEFINED_MODELS[model_key]
    model = model_info["model"]
    engine = model_info.get("engine")
    model_type = model_info.get("type", "unknown")

    if engine == "airllm":
        print(f"🚀 Model: {model_key}")
        print(f"🧠 Mode: {model_type} (AirLLM - slower but powerful)")
    else:
        print(f"🚀 Model: {model_key}")
        print(f"⚡ Mode: {model_type} (Transformers)")

    if not os.getenv("HF_TOKEN"):
        token = input("🔐 Enter HuggingFace token: ")
        login(token)

    config = Config(
        model=model,
        file=None,
        port=args.port,
        public=args.public,
        api_key=args.api_key
    )
    set_global_state(config=config, model=None)

    # Auto fallback
    if engine == "transformers":
        try:
            adapter = HuggingFaceAdapter(model)
            adapter.load()
        except RuntimeError:
            print("⚠️ Switching to AirLLM due to memory limits...")
            print("⚠️ Large model detected.")
            print("⏳ Expect slower responses (10-60 seconds).")
            adapter = AirLLMAdapter(model)
            adapter.load()
    else:
        print("⚠️ Large model detected.")
        print("⏳ Expect slower responses (10-60 seconds).")
        adapter = AirLLMAdapter(model)
        adapter.load()

    state = get_global_state()
    state.adapter = adapter
    print("Model loaded successfully.")

    if config.public:
        time.sleep(2)
        start_tunnel(config.port)

    # Start FastAPI server
    app = create_app()
    print(f"Starting server on port {args.port}...")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
