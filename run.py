import subprocess
import os
import sys
import time
import webbrowser
import socket

def is_backend_ready(host: str = "127.0.0.1", port: int = 8000) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except Exception:
        return False

def run():
    # Ensure we are running from the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    host = "127.0.0.1"
    port = 8000
    app_url = f"http://{host}:{port}"
    
    backend_dir = os.path.join(project_root, 'backend')
    model_path = os.path.join(backend_dir, 'phishing_model.pkl')
    
    # Check if model exists
    if not os.path.exists(model_path):
        print("Model not found. Initializing training...")
        train = subprocess.run([sys.executable, os.path.join(backend_dir, 'train_model.py')])
        if train.returncode != 0:
            raise SystemExit("Training failed. Fix the error above, then re-run `python run.py`.")
    
    print("Starting FastAPI Backend...")
    if "WindowsApps" in (sys.executable or ""):
        print(f"Note: Python executable is `{sys.executable}`.")
        print("If startup fails, install a full Python from python.org and disable Windows 'App execution aliases' for Python.")
    kwargs = {}
    if os.name == 'nt':
        kwargs['creationflags'] = 0x08000000 # CREATE_NO_WINDOW

    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "backend.main:app", 
        "--host", host, "--port", str(port)
    ], **kwargs)
    
    print("Waiting for backend to be responsive...")
    ready = False
    for _ in range(30): # Wait up to 30 seconds
        if backend_process.poll() is not None:
            raise SystemExit(
                "Backend failed to start (uvicorn exited early). "
                "Common causes: missing dependencies, port 8000 in use, or import error. "
                "Check the terminal logs above."
            )
        if is_backend_ready(host=host, port=port):
            ready = True
            break
        time.sleep(1)

    if not ready:
        backend_process.terminate()
        raise SystemExit(
            "Backend did not become ready on port 8000 within 30 seconds. "
            "Check firewall/antivirus and ensure nothing blocks `127.0.0.1:8000`."
        )
    
    print("Opening Astronomia Dashboard...")
    try:
        webbrowser.open(app_url)
    except Exception:
        pass
    
    print("\n" + "="*50)
    print("AI PHISHING DETECTOR IS READY")
    print(f"App: {app_url}")
    print(f"Health: {app_url}/api/health")
    print("="*50 + "\n")
    
    try:
        # Keep the script running to keep the backend alive
        backend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping AI Phishing Detector...")
        backend_process.terminate()

if __name__ == "__main__":
    run()
