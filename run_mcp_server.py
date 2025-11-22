"""
MCP Server Wrapper - Guarantees correct Python path

This wrapper ensures the project root is in sys.path before importing.
"""

import sys
import os
from pathlib import Path

# CRITICAL: Add project root to sys.path FIRST
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set MCP mode
os.environ['SMART_TRADE_MCP_MODE'] = 'true'

# Now import and run server
if __name__ == "__main__":
    try:
        from src.mcp_server.server import main
        main()
    except Exception as e:
        # Print to stderr so it shows in Claude logs
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
