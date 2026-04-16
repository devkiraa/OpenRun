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

def main():
    if len(sys.argv) == 1 or (
        len(sys.argv) > 1 and sys.argv[1] not in ["serve", "run", "-v", "--version", "-h", "--help"]
    ):
        banner = load_banner()

        print("\n\033[96m" + banner + "\033[0m")
        print(f"\033[92m🚀 OpenRun v{__version__}\033[0m")
        print("\033[90mTurn any Python AI model into an OpenAI API\033[0m\n")
        print("👨‍💻 Developed by \033[93mdevkiraa\033[0m\n")
        return

    parser = argparse.ArgumentParser(description="OpenRun - Target any local AI model via an OpenAI-compatible API")
    parser.add_argument("-v", "--version", action="store_true", help="Show OpenRun version")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

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

    args = parser.parse_args()

    if args.version:
        print(f"\033[92mOpenRun v{__version__}\033[0m")
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
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
