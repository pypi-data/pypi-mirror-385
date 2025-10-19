#!/usr/bin/env python3
"""Entry point for the D365FO MCP Server."""

import asyncio
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any, Dict

from d365fo_client import __version__
from d365fo_client.mcp import D365FOMCPServer


def setup_logging(level: str = "INFO") -> None:
    """Set up logging for the MCP server with 24-hour log rotation.

    Args:
        level: Logging level
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Get log file path from environment variable or use default
    log_file_path = os.getenv("D365FO_LOG_FILE")
    
    if log_file_path:
        # Use custom log file path from environment variable
        log_file = Path(log_file_path)
        # Ensure parent directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Use default log file path
        log_dir = Path.home() / ".d365fo-mcp" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "mcp-server.log"

    # Clear existing handlers to avoid duplicate logging
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create rotating file handler - rotates every 24 hours (midnight)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_file),
        when='midnight',        # Rotate at midnight
        interval=1,             # Every 1 day
        backupCount=30,         # Keep 30 days of logs
        encoding='utf-8',       # Use UTF-8 encoding
        utc=False              # Use local time for rotation
    )
    file_handler.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def load_config() -> Dict[str, Any]:
    """Load configuration from environment and config files.
    
    Handles three startup scenarios:
    1. No environment variables: Profile-only mode
    2. D365FO_BASE_URL only: Default auth mode
    3. Full variables: Client credentials mode

    Returns:
        Configuration dictionary with startup_mode indicator
    """
    config = {}
    
    # Get environment variables
    base_url = os.getenv("D365FO_BASE_URL")
    client_id = os.getenv("D365FO_CLIENT_ID")
    client_secret = os.getenv("D365FO_CLIENT_SECRET")
    tenant_id = os.getenv("D365FO_TENANT_ID")
    
    # Determine startup mode based on available environment variables
    if not base_url:
        # Scenario 1: No environment variables - profile-only mode
        config["startup_mode"] = "profile_only"
        config["has_base_url"] = False
        logging.info("Startup mode: profile-only (no D365FO_BASE_URL provided)")
        
    elif base_url and not (client_id and client_secret and tenant_id):
        # Scenario 2: Only base URL - default authentication
        config["startup_mode"] = "default_auth"
        config["has_base_url"] = True
        config.setdefault("default_environment", {})["base_url"] = base_url
        config["default_environment"]["use_default_credentials"] = True
        logging.info("Startup mode: default authentication (D365FO_BASE_URL provided)")
        
    else:
        # Scenario 3: Full credentials - client credentials authentication
        config["startup_mode"] = "client_credentials"
        config["has_base_url"] = True
        config.setdefault("default_environment", {}).update({
            "base_url": base_url,
            "client_id": client_id,
            "client_secret": client_secret,
            "tenant_id": tenant_id,
            "use_default_credentials": False
        })
        logging.info("Startup mode: client credentials (full D365FO environment variables provided)")

    return config


async def async_main() -> None:
    """Async main entry point for the MCP server."""
    try:
        # Set up logging first based on environment variable
        log_level = os.getenv("D365FO_LOG_LEVEL", "INFO")
        setup_logging(log_level)
        
        # Print server version at startup
        logging.info(f"D365FO MCP Server v{__version__}")
        
        # Load configuration
        config = load_config()

        # Create and run the MCP server
        server = D365FOMCPServer(config)

        logging.info("Starting D365FO MCP Server...")
        await server.run()

    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the MCP server."""
    # Ensure event loop compatibility across platforms
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass  # Graceful shutdown


if __name__ == "__main__":
    main()
