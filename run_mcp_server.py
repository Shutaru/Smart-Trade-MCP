"""
MCP Server Wrapper with Enhanced Logging

Provides better error diagnostics for Claude Desktop integration.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set MCP mode
os.environ['SMART_TRADE_MCP_MODE'] = 'true'

# Log to file for debugging
log_file = Path.home() / "smart_trade_mcp_startup.log"

try:
    with open(log_file, 'w') as f:
        f.write("=== SMART TRADE MCP SERVER STARTUP ===\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"CWD: {os.getcwd()}\n")
        f.write(f"Project Root: {project_root}\n")
        f.write(f"sys.path: {sys.path}\n\n")
        
        f.write("Attempting to import server...\n")
        f.flush()
        
        from src.mcp_server.server import main
        
        f.write("Import successful! Starting server...\n")
        f.flush()
        
        main()
        
except Exception as e:
    with open(log_file, 'a') as f:
        import traceback
        f.write(f"\nERROR: {e}\n")
        f.write(f"Traceback:\n{traceback.format_exc()}\n")
    
    # Re-raise to show in Claude Desktop logs
    raise
