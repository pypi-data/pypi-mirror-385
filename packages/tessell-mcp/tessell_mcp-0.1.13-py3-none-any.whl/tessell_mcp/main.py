"""
main.py - Local/STDIO Entrypoint for Tessell MCP Server

This file serves as the entry point for running the Tessell MCP (Model Context Protocol) server in local or stdio mode.

Key Points:
- This entrypoint is intended for local development, testing, and integration with MCP clients (such as Cursor or Visual Studio Code).
- It runs the MCP server in stdio mode, allowing direct communication with local tools and editors.
- All business logic, tool registration, and server configuration are handled via imports from the main MCP server and tools modules.
- For cloud/serverless deployment (e.g., AWS Lambda), use `app.py` instead.

See the README for more details on running in different modes.
"""

import logging
import argparse
import sys
from mcp_core import app_config

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Tessell MCP Server")
parser.add_argument("--app-family", type=str, required=False, help="Comma-separated list of app families to run (service, database, governance)")
parser.add_argument("--readonly-db", action="store_true", help="Run in readonly DB mode")
args, unknown = parser.parse_known_args()

# Set global config
app_config.set_readonly_db(args.readonly_db)

# Parse app_family into a list (if provided)
if args.app_family and args.app_family.strip():
    app_families = [fam.strip() for fam in args.app_family.split(",") if fam.strip()]
else:
    app_families = ["service", "database", "governance"]

# Import docs tool by default, not restricted through app_families
from mcp_core.tools.docs import *

# Conditional imports based on app families
if "service" in app_families:
    from mcp_core.tools.service.availability_machine import *
    from mcp_core.tools.service.services import *
if "database" in app_families:
    from mcp_core.tools.database.database import *
if "governance" in app_families:
    # TODO: Import governance tools when available
    pass

from mcp_core.mcp_server import mcp

# Configure root logger for the package (can be customized further)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info(f"Starting Tessell MCP server (local/stdio mode) with app-family={args.app_family}, readonly_db={args.readonly_db}...")
    mcp.run()

if __name__ == "__main__":
    main()
