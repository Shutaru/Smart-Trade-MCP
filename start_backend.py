#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Start FastAPI Backend Server

Simple script to start the Smart-Trade API server.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Start the FastAPI backend server."""
    
    # Get project root
    project_root = Path(__file__).parent
    
    print("=" * 80)
    print("SMART-TRADE API - STARTING SERVER")
    print("=" * 80)
    print(f"Project Root: {project_root}")
    print("API Version: 3.0.0")
    print("=" * 80)
    
    # Start uvicorn server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ], cwd=project_root, check=True)
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("SERVER STOPPED")
        print("=" * 80)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
