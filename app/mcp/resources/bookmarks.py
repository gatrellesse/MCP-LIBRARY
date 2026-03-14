from app.mcp.server import mcp
from app.db.qdrant import BookQdrant
from pydantic import Field
from typing import Annotated, Literal


# Title  = Annotated[str, Field(min_length=1, max_length=300)]
# Author = Annotated[str, Field(min_length=1, max_length=200)]
# Genre  = Annotated[str, Field(min_length=1, max_length=100)]
Status = Literal["wanting", "reading", "finished"]

@mcp.resource("bookmarks://user/{user_id}")
async def get_user_books(user_id: str):
    """Full reading list for a user."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_user_books(user_id=user_id)


@mcp.resource("bookmarks://user/{user_id}/{status}")
async def get_user_books_by_status(user_id: str, status: Status):
    """User's books filtered by status: wanting, reading, or finished."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_user_books(user_id=user_id, status=status)
