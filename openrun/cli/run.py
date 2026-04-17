import time
import os
import sys
import questionary
from openrun.models.registry import PREDEFINED_MODELS

def run_predefined(args):
    if not args.model_name:
        is_colab = False
        try:
            import google.colab
            is_colab = True
        except ImportError:
            pass

        model_keys = list(PREDEFINED_MODELS.keys())
        
        if is_colab:
            print("\n\033[1mSelect a model to run:\033[0m")
            header = f"\033[4m{'Model Name'.ljust(14)} │ {'Size'.rjust(4)} │ Ctx: {'Limit'.rjust(5)} │ {'Tokens/sec'.rjust(11)} │ Engine\033[0m"
            print(f"      {header}")
            
            for i, key in enumerate(model_keys, 1):
                info = PREDEFINED_MODELS[key]
                engine = info.get("engine", "transformers")
                size = info.get("size", "N/A")
                ctx = info.get("context", "N/A")
                speed = info.get("speed", "N/A")
                f_name = key.ljust(14)
                f_size = size.rjust(4)
                f_ctx = ctx.rjust(5)
                f_speed = speed.rjust(11)
                f_engine = f"[{engine}]"
                print(f"  \033[96m[{i}]\033[0m {f_name} │ {f_size} │ Ctx: {f_ctx} │ {f_speed} │ {f_engine}")
            
            while True:
                try:
                    choice = input("\n\033[93m❯\033[0m Select number or model name: ").strip().lower()
                    if not choice:
                        continue
                    if choice.isdigit() and 1 <= int(choice) <= len(model_keys):
                        args.model_name = model_keys[int(choice) - 1]
                        break
                    elif choice in PREDEFINED_MODELS:
                        args.model_name = choice
                        break
                    else:
                        print("\033[91m❌ Invalid selection. Try again.\033[0m")
                except EOFError:
                    print("\n\033[93m[INFO] Exiting interactive menu.\033[0m")
                    return
            
            while True:
                try:
                    print("\n\033[1mChoose execution mode:\033[0m")
                    print("  \033[96m[1]\033[0m 🌐 Run API Server (OpenAI Compatible)")
                    print("  \033[96m[2]\033[0m 💬 Local Chat (Interactive Terminal)")
                    choice = input("\n\033[93m❯\033[0m Select number [1-2]: ").strip()
                    if not choice:
                        continue
                    if choice == "1":
                        args.run_mode = "api"
                        break
                    elif choice == "2":
                        args.run_mode = "chat"
                        break
                    else:
                        print("\033[91m❌ Invalid selection. Try again.\033[0m")
                except EOFError:
                    print("\n\033[93m[INFO] Exiting interactive menu.\033[0m")
                    return
        else:
            choices = []
            
            # Add column headers as an unselectable separator
            header = f"{'Model Name'.ljust(14)} │ {'Size'.rjust(4)} │ Ctx: {'Limit'.rjust(5)} │ {'Tokens/sec'.rjust(11)} │ Engine"
            choices.append(questionary.Separator(header))
            
            for key in model_keys:
                info = PREDEFINED_MODELS[key]
                engine = info.get("engine", "transformers")
                size = info.get("size", "N/A")
                ctx = info.get("context", "N/A")
                speed = info.get("speed", "N/A")
                
                # Format columns beautifully
                f_name = key.ljust(14)
                f_size = size.rjust(4)
                f_ctx = ctx.rjust(5)
                f_speed = speed.rjust(11)
                f_engine = f"[{engine}]"
                
                display_title = f"{f_name} │ {f_size} │ Ctx: {f_ctx} │ {f_speed} │ {f_engine}"
                choices.append(questionary.Choice(display_title, value=key))
                
            try:
                selected_model = questionary.select(
                    "Select a model to run:",
                    choices=choices,
                    instruction="(Use arrow keys)",
                    pointer="❯",
                    style=questionary.Style([
                        ('qmark', 'fg:yellow bold'),
                        ('question', 'bold'),
                        ('answer', 'fg:cyan bold'),
                        ('pointer', 'fg:yellow bold'),
                        ('highlighted', 'fg:cyan bold'),
                        ('selected', 'fg:cyan'),
                    ])
                ).ask()
                
                if not selected_model:
                    print("\n\033[93m[INFO] Exiting interactive menu.\033[0m")
                    return
                    
                args.model_name = selected_model
                
                # Step 2: Select Mode
                mode_choice = questionary.select(
                    "Choose execution mode:",
                    choices=[
                        questionary.Choice("🌐 Run API Server (OpenAI Compatible)", value="api"),
                        questionary.Choice("💬 Local Chat (Interactive Terminal)", value="chat")
                    ],
                    instruction="(Use arrow keys)",
                    pointer="❯",
                    style=questionary.Style([
                        ('qmark', 'fg:yellow bold'),
                        ('question', 'bold'),
                        ('answer', 'fg:cyan bold'),
                        ('pointer', 'fg:yellow bold'),
                        ('highlighted', 'fg:cyan bold'),
                        ('selected', 'fg:cyan'),
                    ])
                ).ask()
                
                if not mode_choice:
                    print("\n\033[93m[INFO] Exiting interactive menu.\033[0m")
                    return
                args.run_mode = mode_choice
                
            except KeyboardInterrupt:
                print("\n\033[93m[INFO] Exiting interactive menu.\033[0m")
                return

    # Keep args.run_mode fallback for direct CLI invocation
    if not hasattr(args, 'run_mode'):
        args.run_mode = "api"

    model_key = args.model_name.lower()
    
    if model_key not in PREDEFINED_MODELS:
        print(f"❌ Error: Predefined model '{model_key}' not found.")
        print(f"Available models: {', '.join(PREDEFINED_MODELS.keys())}")
        return

    print("\n\033[90m[0/3] Loading dependencies and core modules... Please wait.\033[0m")
    
    # Deferred heavy imports to make the prompt load instantly
    import uvicorn
    from huggingface_hub import login
    from openrun.core.config import Config
    from openrun.core.state import set_global_state, get_global_state
    from openrun.network.server import create_app
    from openrun.network.tunnel import start_tunnel
    from openrun.adapters.huggingface import HuggingFaceAdapter
    from openrun.adapters.airllm import AirLLMAdapter
    from openrun.adapters.ollama import OllamaAdapter

    model_info = PREDEFINED_MODELS[model_key]
    model = model_info["model"]
    engine = model_info.get("engine")
    model_type = model_info.get("type", "unknown")

    if engine == "airllm":
        print(f"\033[96m➤\033[0m \033[1mModel :\033[0m {model_key}")
        print(f"\033[96m➤\033[0m \033[1mEngine:\033[0m \033[93m{model_type} (AirLLM)\033[0m")
    elif engine == "ollama":
        print(f"\033[96m➤\033[0m \033[1mModel :\033[0m {model_key}")
        print(f"\033[96m➤\033[0m \033[1mEngine:\033[0m \033[95m{model_type} (Ollama)\033[0m")
    else:
        print(f"\033[96m➤\033[0m \033[1mModel :\033[0m {model_key}")
        print(f"\033[96m➤\033[0m \033[1mEngine:\033[0m \033[92m{model_type} (Transformers)\033[0m")

    # Tokens are only for HF-based models
    if engine != "ollama":
        token = os.getenv("HF_TOKEN")
        is_colab_runtime = False

        # In Colab, prefer a saved secret before prompting.
        if not token:
            try:
                import google.colab
                from google.colab import userdata
                is_colab_runtime = True
                try:
                    token = userdata.get("HF_TOKEN")
                    if token:
                        print("\033[92m✔ Found HF_TOKEN in Colab secrets.\033[0m")
                except Exception:
                    token = None
            except ImportError:
                pass

        if token:
            login(token)
        else:
            if is_colab_runtime:
                print("\033[90m[INFO] No saved HF_TOKEN found in Colab secrets.\033[0m")
            import getpass
            token = getpass.getpass("\033[93m🔐\033[0m Enter HuggingFace token: ")
            if token:
                login(token)

    config = Config(
        model=model,
        file=None,
        port=args.port,
        public=True,
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
    elif engine == "ollama":
        print(f"\033[90m[2/3] Connecting to local Ollama ({model})...\033[0m")
        adapter = OllamaAdapter(model)
        adapter.load()
    else:
        print(f"\033[90m[2/3] Initializing {model} into memory...\033[0m")
        print("\033[93m⏳ Large model detected. Expect slower responses.\033[0m")
        adapter = AirLLMAdapter(model)
        adapter.load()

    state = get_global_state()
    state.adapter = adapter
    print("\033[92m✔ Model loaded successfully.\033[0m")

    if args.run_mode == "chat":
        print(f"\n\033[90m[3/3] Booting API server on port {args.port} (background)...\033[0m")
        app = create_app()
        print(f"\n\033[92m🚀 OpenRun is LIVE!\033[0m")
        print(f"📡 \033[1mEndpoint:\033[0m http://localhost:{args.port}/v1/chat/completions")
        print(f"🧪 \033[1mPlayground:\033[0m http://localhost:{args.port}/chat")

        # Start server in background so local terminal chat can run simultaneously.
        import threading

        def _run_background_server():
            try:
                uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="warning")
            except BaseException:
                pass

        server_thread = threading.Thread(target=_run_background_server, daemon=True)
        server_thread.start()

        time.sleep(1)
        start_tunnel(config.port)

        print(f"\n\033[92m💬 Starting Local Chat with {model}...\033[0m")
        print("\033[90mType 'exit' or 'quit' to stop.\033[0m\n")
        messages = []
        while True:
            try:
                user_msg = input("\033[94mYou:\033[0m ")
                if user_msg.lower() in ['exit', 'quit']:
                    break
                if not user_msg.strip():
                    continue
                
                messages.append({"role": "user", "content": user_msg})
                print("\033[92mAI:\033[0m ", end="", flush=True)
                
                response_text = ""
                try:
                    for chunk in adapter.stream(messages):
                        print(chunk, end="", flush=True)
                        response_text += chunk
                    print()
                except (NotImplementedError, AttributeError):
                    # Fallback if the adapter doesn't properly support streaming yet
                    response_text = adapter.generate(messages)
                    print(response_text)
                
                messages.append({"role": "assistant", "content": response_text})
                print()
            except (KeyboardInterrupt, EOFError):
                break
        print("\n\033[93m[INFO] Exiting chat.\033[0m")
        return

    print(f"\n\033[90m[3/3] Booting API server on port {args.port}...\033[0m")
    time.sleep(1)
    start_tunnel(config.port)

    # Start FastAPI server
    app = create_app()
    
    print(f"\n\033[92m🚀 OpenRun is LIVE!\033[0m")
    print(f"📡 \033[1mEndpoint:\033[0m http://localhost:{args.port}/v1/chat/completions")
    
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="warning")
    except KeyboardInterrupt:
        print("\n\033[93m[INFO] Shutting down OpenRun server cleanly...\033[0m")
    except BaseException as e:
        if e.__class__.__name__ in ("CancelledError", "KeyboardInterrupt"):
            print("\n\033[93m[INFO] Shutting down OpenRun server cleanly...\033[0m")
        else:
            raise
