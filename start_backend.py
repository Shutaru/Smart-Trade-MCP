"""
Start Smart Trade MCP Backend API

Simple script to run the FastAPI backend with uvicorn.
"""

import subprocess
import sys

print("=" * 80)
print("STARTING SMART TRADE MCP BACKEND API")
print("=" * 80)
print()
print("Backend will be available at: http://localhost:8000")
print("API docs: http://localhost:8000/docs")
print()
print("Press CTRL+C to stop")
print()

try:
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "src.api.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])
except KeyboardInterrupt:
    print("\n\nBackend stopped.")
