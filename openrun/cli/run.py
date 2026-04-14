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
        print(f"\033[96m➤\033[0m \033[1mModel :\033[0m {model_key}")
        print(f"\033[96m➤\033[0m \033[1mEngine:\033[0m \033[93m{model_type} (AirLLM)\033[0m")
    else:
        print(f"\033[96m➤\033[0m \033[1mModel :\033[0m {model_key}")
        print(f"\033[96m➤\033[0m \033[1mEngine:\033[0m \033[92m{model_type} (Transformers)\033[0m")

    if not os.getenv("HF_TOKEN"):
        token = input("\033[93m🔐\033[0m Enter HuggingFace token: ")
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
    print(f"\n\033[90m[1/3] Loading configuration...\033[0m")
    if engine == "transformers":
        try:
            print(f"\033[90m[2/3] Initializing {model} into memory...\033[0m")
            adapter = HuggingFaceAdapter(model)
            adapter.load()
        except RuntimeError:
            print("\033[93m⚠️ Memory limited! Switching to AirLLM engine...\033[0m")
            print("\033[93m⏳ Expect slower responses (10-60 seconds)\033[0m")
            adapter = AirLLMAdapter(model)
            adapter.load()
    else:
        print(f"\033[90m[2/3] Initializing {model} into memory...\033[0m")
        print("\033[93m⏳ Large model detected. Expect slower responses.\033[0m")
        adapter = AirLLMAdapter(model)
        adapter.load()

    state = get_global_state()
    state.adapter = adapter
    print("\033[92m✔ Model loaded successfully.\033[0m")

    print(f"\n\033[90m[3/3] Booting API server on port {args.port}...\033[0m")
    if config.public:
        time.sleep(1)
        start_tunnel(config.port)

    # Start FastAPI server
    app = create_app()
    
    print(f"\n\033[92m🚀 OpenRun is LIVE!\033[0m")
    print(f"📡 \033[1mEndpoint:\033[0m http://localhost:{args.port}/v1/chat/completions")
    
    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="warning")
