import uvicorn
from core.config import Config
from core.state import set_global_state
from network.server import create_app
from network.tunnel import start_tunnel
from model.loader import load_model

def run_serve(args):
    print("--- OpenRun Serve ---")
    print(f"Model  : {args.model}")
    print(f"File   : {args.file}")
    print(f"Port   : {args.port}")
    print(f"Public : {args.public}")
    print(f"API Key: {args.api_key}")

    # Initialize config and state
    config = Config(
        model=args.model,
        file=args.file,
        port=args.port,
        public=args.public,
        api_key=args.api_key
    )
    set_global_state(config=config, model=None)

    # Load model via loader
    load_model(config)

    # Start Cloudflare tunnel if requested
    if config.public:
        import time
        time.sleep(2)
        start_tunnel(config.port)

    # Start FastAPI server
    app = create_app()
    print(f"Starting server on port {args.port}...")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
