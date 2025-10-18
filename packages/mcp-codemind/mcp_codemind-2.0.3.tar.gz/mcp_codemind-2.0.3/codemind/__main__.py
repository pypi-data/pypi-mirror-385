#!/usr/bin/env python3
"""CodeMind - Multi-Workspace MCP Memory Server Entry Point.

This allows running CodeMind as a module: python -m codemind
"""

import os
import sys
import warnings
import logging
from datetime import datetime
from pathlib import Path

# Suppress transformers/sentence-transformers progress bars and warnings for clean MCP output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Suppress FastMCP startup banner for clean VS Code MCP output
os.environ['FASTMCP_QUIET'] = '1'

# Setup session logging to .codemind/logs/
session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = Path(".codemind/logs")
log_dir.mkdir(parents=True, exist_ok=True)
session_log_file = log_dir / f"session_{session_id}.log"

# Configure logging to both console and session file with UTF-8 encoding
file_handler = logging.FileHandler(session_log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# For MCP stderr output, use minimal logging to avoid VS Code warnings
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setLevel(logging.WARNING)  # Only show warnings/errors to MCP client
stream_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)

logger = logging.getLogger(__name__)
logger.info(f"Session logging to: {session_log_file}")

# Import FastMCP
from fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("CodeMind")

# Register all 20 tools from the package
from codemind.tools import register_all_tools
register_all_tools(mcp)

logger.info("All 20 CodeMind tools registered successfully")
logger.info("Server ready - waiting for MCP client connections...")

# Start the server
if __name__ == "__main__":
    mcp.run()
