import logging

from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),        # stderr — stdout is reserved for MCP protocol
        logging.FileHandler("mcp.log"),
    ],
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.WARNING)
logging.getLogger("fastembed").setLevel(logging.WARNING)

mcp = FastMCP(
    name="MCP-Book",
    instructions= "A personal book library. Use search_library to find books by meaning, "
        "not just keywords. Always use add_bookmark before update_book_status. "
        "user_id is always the authenticated user's identifier."
    )
