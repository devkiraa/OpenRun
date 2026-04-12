import argparse
import sys
from openrun.cli.serve import run_serve

def main():
    parser = argparse.ArgumentParser(description="OpenRun - Target any local AI model via an OpenAI-compatible API")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the OpenAI-compatible server")
    serve_parser.add_argument("--model", type=str, help="Name of the model to load")
    serve_parser.add_argument("--file", type=str, help="Path to custom model file")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    serve_parser.add_argument("--public", action="store_true", help="Expose server publicly via Cloudflare")
    serve_parser.add_argument("--api-key", type=str, help="Require API key for requests")

    args = parser.parse_args()

    if args.command == "serve":
        run_serve(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
