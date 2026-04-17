import time
import uvicorn

from openrun.core.config import Config
from openrun.core.state import set_global_state
from openrun.network.server import create_app
from openrun.network.tunnel import start_tunnel


def run_chat(args):
    public_enabled = not getattr(args, "no_public", False)

    config = Config(
        model=None,
        file=None,
        port=args.port,
        public=public_enabled,
        api_key=args.api_key,
    )
    set_global_state(config=config, model=None, adapter=None)

    app = create_app()

    print("\n\033[92m🚀 OpenRun Chat UI is LIVE!\033[0m")
    print(f"📡 \033[1mLocal API:\033[0m http://localhost:{args.port}/v1/chat/completions")
    print(f"💬 \033[1mLocal UI:\033[0m  http://localhost:{args.port}/chat")

    if public_enabled:
        time.sleep(1)
        start_tunnel(config.port)

    try:
        uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="warning")
    except KeyboardInterrupt:
        print("\n\033[93m[INFO] Shutting down OpenRun chat server cleanly...\033[0m")
