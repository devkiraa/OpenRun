import argparse
import sys
from openrun.cli.serve import run_serve
from openrun import __version__

def main():
    if len(sys.argv) == 1 or (
        len(sys.argv) > 1 and sys.argv[1] not in ["serve", "-v", "--version", "-h", "--help"]
    ):
        print(f"""
\033[96m
 ________  ________  _______   ________   ________  ___  ___  ________      
|\   __  \|\   __  \|\  ___ \ |\   ___  \|\   __  \|\  \|\  \|\   ___  \    
\ \  \|\  \ \  \|\  \ \   __/|\ \  \\ \  \ \  \|\  \ \  \\\  \ \  \\ \  \   
 \ \  \\\  \ \   ____\ \  \_|/_\ \  \\ \  \ \   _  _\ \  \\\  \ \  \\ \  \  
  \ \  \\\  \ \  \___|\ \  \_|\ \ \  \\ \  \ \  \\  \\ \  \\\  \ \  \\ \  \ 
   \ \_______\ \__\    \ \_______\ \__\\ \__\ \__\\ _\\ \_______\ \__\\ \__\
    \|_______|\|__|     \|_______|\|__| \|__|\|__|\|__|\|_______|\|__| \|__|                                  
\033[0m

\033[92m🚀 OpenRun\033[0m
\033[90mTurn any Python AI model into an OpenAI API\033[0m

👨‍💻 Developed by \033[93mdevkiraa\033[0m
""")
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

    args = parser.parse_args()

    if args.version:
        print(f"\033[92mOpenRun v{__version__}\033[0m")
        return

    if args.command == "serve":
        run_serve(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
