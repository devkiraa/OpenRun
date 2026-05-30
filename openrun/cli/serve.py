import uvicorn
from openrun.core.config import Config
from openrun.core.state import set_global_state
from openrun.network.server import create_app
from openrun.network.tunnel import start_tunnel
from openrun.model.loader import load_model

def run_serve(args):
    from openrun.utils.graphics import animate_loading_status, draw_live_dashboard
    
    animate_loading_status("0/3", "Loading dependencies and core modules", duration=1.0)
    
    print(f"\033[96m➤\033[0m \033[1mModel :\033[0m {args.model or 'custom-file'}")
    print(f"\033[96m➤\033[0m \033[1mFile  :\033[0m {args.file or 'none'}")
    print(f"\033[96m➤\033[0m \033[1mPort  :\033[0m {args.port}")

    # Initialize config and state
    animate_loading_status("1/3", "Loading configuration parameters", duration=0.8)
    
    config = Config(
        model=args.model,
        file=args.file,
        port=args.port,
        public=args.public,
        api_key=args.api_key,
        quantize=getattr(args, "quantize", None),
        low_cpu_mem=getattr(args, "low_cpu_mem", False),
        engine=getattr(args, "engine", "transformers"),
        draft_model=getattr(args, "draft_model", None),
    )
    set_global_state(config=config, model=None)

    # Load model via loader
    print(f"\033[90m[2/3] Initializing {args.model or args.file} into memory...\033[0m")
    import sys
    try:
        load_model(config)
    except Exception as e:
        if "Gated Repository" in str(e):
            sys.exit(1)
        raise

    print("\033[92m✔ Model loaded successfully.\033[0m")

    animate_loading_status("3/3", f"Booting API server on port {args.port}", duration=1.2)

    # Start Cloudflare tunnel if requested
    if config.public:
        start_tunnel(config.port)

    # Start FastAPI server
    app = create_app()
    draw_live_dashboard(args.port, config.api_key)
    try:
        uvicorn.run(app, host="0.0.0.0", port=args.port, timeout_keep_alive=65, loop="auto")
    finally:
        # Clear model and free GPU memory cleanly
        from openrun.core.state import get_global_state
        state = get_global_state()
        if state and state.adapter:
            try:
                print("\033[90m🧹 Releasing GPU memory and clearing model resources...\033[0m")
                state.adapter.unload()
                print("\033[92m✔ GPU memory successfully cleared and released.\033[0m")
            except Exception:
                pass
