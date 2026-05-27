import argparse
import sys
import os
from openrun import __version__

def load_banner():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    banner_path = os.path.join(base_dir, "openrun.txt")
    
    try:
        with open(banner_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "OpenRun"

def animate_banner(banner_text):
    import time
    import math
    import sys
    
    try:
        import msvcrt
    except ImportError:
        msvcrt = None
        
    lines = banner_text.splitlines()
    if not lines:
        return
        
    if not sys.stdout.isatty():
        print(banner_text)
        print(f"\033[92m🚀 OpenRun v{__version__}\033[0m")
        print("\033[90mTurn any Python AI model into an OpenAI API\033[0m\n")
        print("👨‍💻 Developed by \033]8;;https://github.com/devkiraa\033\\\033[93mdevkiraa\033[0m\033]8;;\033\\\n")
        return
        
    num_lines = len(lines)
    
    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    
    frame = 0
    try:
        while True:
            screen = []
            screen.append("") # leading newline
            
            # Subtle breathing pulse: overall brightness shifts gently between 0.85 and 1.0
            breath = 0.9 + 0.1 * math.sin(frame * 0.06)
            
            # Phase shifts colors smoothly horizontally over time
            phase = frame * 0.04
            
            for y, line in enumerate(lines):
                colored_line = []
                for x, char in enumerate(line):
                    if char.isspace():
                        colored_line.append(char)
                        continue
                    
                    # Compute flowing horizontal wave position
                    pos = (x / 70.0) - phase
                    
                    # Premium 'Sunset Ember' warm flowing fire palette:
                    # - Deep Crimson (210, 30, 15)
                    # - Fiery Orange (255, 100, 30)
                    # - Gold / Amber (210, 170, 15)
                    # - Copper Bronze (165, 100, 0)
                    r = int((210 + 45 * math.sin(pos * 2 * math.pi)) * breath)
                    g = int((100 + 70 * math.cos(pos * 2 * math.pi)) * breath)
                    b = int((15 + 15 * math.sin(pos * 2 * math.pi)) * breath)
                    
                    r = max(0, min(255, r))
                    g = max(0, min(255, g))
                    b = max(0, min(255, b))
                    
                    colored_line.append(f"\033[38;2;{r};{g};{b}m{char}")
                screen.append("".join(colored_line) + "\033[0m")
            
            # Static metadata
            screen.append(f"\033[92m🚀 OpenRun v{__version__}\033[0m")
            screen.append("\033[90mTurn any Python AI model into an OpenAI API\033[0m\n")
            screen.append("👨‍💻 Developed by \033]8;;https://github.com/devkiraa\033\\\033[93mdevkiraa\033[0m\033]8;;\033\\\n")
            screen.append("\033[90m[ Press any key or Ctrl+C to exit ]\033[0m")
            
            screen_content = "\n".join(screen) + "\n"
            sys.stdout.write(screen_content)
            sys.stdout.flush()
            
            # Exit keypress hook
            if msvcrt and msvcrt.kbhit():
                while msvcrt.kbhit():
                    msvcrt.getch()
                sys.stdout.write(f"\033[{screen_content.count(chr(10))}A")
                sys.stdout.write("\n" + "\n".join(f"\033[96m{l}\033[0m" for l in lines) + "\n")
                sys.stdout.write(f"\033[92m🚀 OpenRun v{__version__}\033[0m\n")
                sys.stdout.write("\033[90mTurn any Python AI model into an OpenAI API\033[0m\n\n")
                sys.stdout.write("👨‍💻 Developed by \033]8;;https://github.com/devkiraa\033\\\033[93mdevkiraa\033[0m\033]8;;\033\\\n\n")
                sys.stdout.flush()
                break
                
            total_lines = screen_content.count("\n")
            sys.stdout.write(f"\033[{total_lines}A")
            sys.stdout.flush()
            
            frame += 1
            time.sleep(0.03) # smooth 30fps
            
    except KeyboardInterrupt:
        sys.stdout.write(f"\033[{screen_content.count(chr(10))}B")
        sys.stdout.flush()
        print("\n\033[93m[INFO] OpenRun banner animation stopped.\033[0m")
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    try:
        from openrun.utils.windows_path import check_and_add_windows_path
        check_and_add_windows_path()
    except Exception:
        pass

    if len(sys.argv) == 1 or (
        len(sys.argv) > 1 and sys.argv[1] not in ["serve", "run", "chat", "models", "model", "-v", "--version", "--models", "--model", "-h", "--help"]
    ):
        banner = load_banner()
        animate_banner(banner)
        return

    parser = argparse.ArgumentParser(description="OpenRun - Target any local AI model via an OpenAI-compatible API")
    parser.add_argument("-v", "--version", action="store_true", help="Show OpenRun version")
    parser.add_argument("--models", "--model", action="store_true", help="List all available predefined models")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Models command
    models_parser = subparsers.add_parser("models", help="List all available predefined models")
    model_parser = subparsers.add_parser("model", help="List all available predefined models")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the OpenAI-compatible server")
    serve_parser.add_argument("--model", type=str, help="Name of the model to load")
    serve_parser.add_argument("--file", type=str, help="Path to custom model file")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    serve_parser.add_argument("--public", action="store_true", help="Expose server publicly via Cloudflare")
    serve_parser.add_argument("--api-key", type=str, help="Require API key for requests")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a predefined model interactively or directly")
    run_parser.add_argument("model_name", type=str, nargs="?", help="Predefined model name to run (optional, leave blank for interactive menu)")
    run_parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    run_parser.add_argument("--public", action="store_true", help="Expose server publicly via Cloudflare")
    run_parser.add_argument("--api-key", type=str, help="Require API key for requests")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start ChatGPT-like web UI with dynamic model loading")
    chat_parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    chat_parser.add_argument("--api-key", type=str, help="Require API key for requests")
    chat_parser.add_argument("--no-public", action="store_true", help="Disable Cloudflare public URL")

    args = parser.parse_args()

    if args.version:
        print(f"\033[92mOpenRun v{__version__}\033[0m")
        return

    if args.models or args.command in ["models", "model"]:
        from openrun.cli.models_list import list_models
        list_models()
        return

    import asyncio
    
    if args.command == "serve":
        try:
            from openrun.cli.serve import run_serve
            run_serve(args)
        except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
            print("\n\033[93m[INFO] OpenRun Server stopped.\033[0m")
            sys.exit(0)
    elif args.command == "run":
        from openrun.cli.run import run_predefined
        try:
            run_predefined(args)
        except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
            print("\n\033[93m[INFO] OpenRun Server stopped.\033[0m")
            sys.exit(0)
    elif args.command == "chat":
        from openrun.cli.chat import run_chat
        try:
            run_chat(args)
        except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
            print("\n\033[93m[INFO] OpenRun Chat stopped.\033[0m")
            sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
