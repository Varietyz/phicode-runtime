import argparse
import sys
from .http_server import start_server
from .subprocess_handler import PhicodeSubprocessHandler
from ..config.config import ENGINE, SERVER

def main():
    parser = argparse.ArgumentParser(description=f" {SERVER}")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--timeout", type=int, default=30, help="Execution timeout in seconds")

    args = parser.parse_args()

    print(f"🔍 Checking {ENGINE} availability...")
    handler = PhicodeSubprocessHandler()
    info = handler.get_engine_info()

    if not info["success"]:
        print(f"❌ {ENGINE} not available: {info['error']}")
        print(f"💡 Make sure {ENGINE} is installed: pip install phicode")
        sys.exit(1)

    print(f"✅ {ENGINE} Available!")
    print()

    try:
        start_server(args.host, args.port)
    except Exception as e:
        print(f"❌ Failed to start {SERVER}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()