"""
Web server command for ugit.
"""

import os
import webbrowser
from typing import Optional

from ugit.utils.helpers import ensure_repository


def serve(
    port: int = 8000, host: str = "127.0.0.1", open_browser: bool = True
) -> Optional[int]:
    """
    Start the ugit web interface server.

    Args:
        port: Port to run the server on (default: 8000)
        host: Host to bind to (default: 127.0.0.1)
        open_browser: Whether to open browser automatically (default: True)
    """
    try:
        # Check if we're in a ugit repository
        repo = ensure_repository()
        repo_root = repo.path

        print("Starting ugit web interface...")
        print(f"Repository: {repo_root}")
        print(f"Server: http://{host}:{port}")
        print("Press Ctrl+C to stop the server")

        # Change to repository directory
        os.chdir(repo_root)

        # Import and start the web server
        try:
            import uvicorn

            from ugit.web.server import create_app
        except ImportError:
            print("Error: Web dependencies not installed.")
            print("Install ugit with web support using:")
            print("  pip install ugit-cli[web]")
            print()
            print("Or install dependencies manually:")
            print("  pip install fastapi uvicorn jinja2 python-multipart aiofiles")
            return 1

        # Create the FastAPI app
        app = create_app(repo_root)

        # Open browser if requested
        if open_browser:

            def open_browser_delayed() -> None:
                import threading
                import time

                def delayed_open() -> None:
                    time.sleep(1.5)  # Wait for server to start
                    webbrowser.open(f"http://{host}:{port}")

                thread = threading.Thread(target=delayed_open)
                thread.daemon = True
                thread.start()

            open_browser_delayed()

        # Start the server
        uvicorn.run(app, host=host, port=port, log_level="info", access_log=True)
        return 0

    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1


if __name__ == "__main__":
    serve()
