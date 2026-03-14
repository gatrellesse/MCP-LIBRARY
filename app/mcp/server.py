import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).parents[2] / ".env.library")

def _resolve_user_id() -> str:
    token = os.environ.get("USER_TOKEN", "")
    for key, value in os.environ.items():
        if key.startswith("TOKEN_") and value == token:
            return key[len("TOKEN_"):]
    raise RuntimeError("Invalid or missing USER_TOKEN — access denied.")

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


USER_ID = _resolve_user_id()

mcp = FastMCP(
    name="MCP-Book",
    instructions="A personal book library."
    )
