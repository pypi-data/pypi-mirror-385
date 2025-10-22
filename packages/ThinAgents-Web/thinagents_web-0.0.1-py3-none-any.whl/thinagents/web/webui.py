import webbrowser
import uvicorn
import threading
import subprocess
import time
import sys
from typing import Optional
from pathlib import Path


class WebUI:
    def __init__(
        self, 
        agent, 
        host: str = "127.0.0.1", 
        port: int = 8000,
        dev_mode: bool = False
    ):
        self.agent = agent
        self.host = host
        self.port = port
        self.dev_mode = dev_mode
        self._frontend_process = None

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        open_browser: bool = True,
        dev_mode: Optional[bool] = None,
    ):
        host = host or self.host
        port = port or self.port
        dev_mode = dev_mode if dev_mode is not None else self.dev_mode
        
        frontend_src = Path(__file__).parent.parent / "frontend" / "src"
        has_source = frontend_src.exists()
        
        if dev_mode and has_source:
            self._run_dev_mode(host, port, open_browser)
        else:
            self._run_prod_mode(host, port, open_browser)

    def _run_dev_mode(self, host: str, port: int, open_browser: bool):
        frontend_port = 5173
        
        print("\n🚀 ThinAgents Web UI (DEV MODE)")
        print(f"📍 Backend: http://{host}:{port}")
        print(f"📍 Frontend: http://{host}:{frontend_port}")
        print("\nPress CTRL+C to stop.\n")

        self._start_backend_thread(host, port)
        time.sleep(2)
        self._start_frontend_dev(host, frontend_port)

        if open_browser:
            threading.Timer(3, lambda: webbrowser.open(f"http://{host}:{frontend_port}")).start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            self.stop()
            sys.exit(0)

    def _run_prod_mode(self, host: str, port: int, open_browser: bool):
        from .backend.server import create_app
        
        build_dir = Path(__file__).parent / "ui" / "build"
        if not build_dir.exists():
            print("❌ UI build not found!")
            print("   Run: python scripts/build_ui.py")
            sys.exit(1)

        app = create_app(self.agent)

        print("\n🚀 ThinAgents Web UI")
        print(f"📍 Server: http://{host}:{port}")
        print("\nPress CTRL+C to stop.\n")

        if open_browser:
            threading.Timer(1.5, lambda: webbrowser.open(f"http://{host}:{port}")).start()

        uvicorn.run(app, host=host, port=port, log_level="warning")

    def _start_backend_thread(self, host: str, port: int):
        from .backend.server import create_app
        app = create_app(self.agent)

        def run_backend():
            uvicorn.run(app, host=host, port=port, log_level="warning")

        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()

    def _start_frontend_dev(self, host: str, port: int):
        frontend_dir = Path(__file__).parent.parent / "frontend"
        
        try:
            self._frontend_process = subprocess.Popen(
                ["pnpm", "run", "dev", "--host", host, "--port", str(port)],
                cwd=frontend_dir,
            )
        except FileNotFoundError:
            print("❌ 'pnpm' not found. Install: npm install -g pnpm")
            sys.exit(1)

    def stop(self):
        if self._frontend_process:
            self._frontend_process.terminate()
            try:
                self._frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._frontend_process.kill()
        
        print("✅ Stopped")

