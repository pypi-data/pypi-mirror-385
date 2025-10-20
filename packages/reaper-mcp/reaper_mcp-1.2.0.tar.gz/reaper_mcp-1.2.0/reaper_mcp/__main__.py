import argparse
import logging
from reaper_mcp.mcp_core import mcp

# Configure logging to help debug validation errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import tool modules so their @mcp.tool functions register
from reaper_mcp import project as _project  # noqa: F401
from reaper_mcp import tracks as _tracks  # noqa: F401
from reaper_mcp import tempo as _tempo  # noqa: F401
from reaper_mcp import midi as _midi  # noqa: F401
from reaper_mcp import fx as _fx  # noqa: F401
from reaper_mcp import samples as _samples  # noqa: F401


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Reaper MCP server with selectable transport")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http", "ws", "websocket"],
        default="stdio",
        help="Transport to use for MCP server (default: stdio)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host for network transports")
    parser.add_argument("--port", type=int, default=8000, help="Bind port for network transports")
    parser.add_argument(
        "--path",
        default=None,
        help="URL path for HTTP/SSE/Websocket transports (only passed if supported)",
    )
    parser.add_argument(
        "--allow-origin",
        dest="allow_origins",
        action="append",
        default=None,
        help="Allowed CORS origin (can be specified multiple times). Only passed if supported.",
    )
    return parser.parse_args()


def main():
    """Main entry point for the reaper-mcp CLI."""
    args = _parse_args()

    # Build kwargs for mcp.run without signature inspection; FastMCP.run accepts **kwargs
    kw = {"show_banner": False}

    # Normalize some transport aliases
    transport = args.transport
    if transport == "http":
        # Many MCP servers implement HTTP via SSE; prefer 'sse'
        transport = "sse"
    if transport == "websocket":
        transport = "ws"

    kw["transport"] = transport

    # Add networking options for non-stdio transports.
    if transport != "stdio":
        kw["host"] = args.host
        kw["port"] = args.port
        if args.path is not None:
            kw["path"] = args.path
        #if args.allow_origins is not None:
            #kw["allow_origins"] = args.allow_origins

    # Start the MCP server
    mcp.run(**kw)


if __name__ == "__main__":
    main()
