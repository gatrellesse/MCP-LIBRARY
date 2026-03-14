from app.mcp.server import mcp, USER_ID
from app.db.qdrant import BookQdrant
from pydantic import Field
from typing import Annotated, Literal


# Title  = Annotated[str, Field(min_length=1, max_length=300)]
# Author = Annotated[str, Field(min_length=1, max_length=200)]
# Genre  = Annotated[str, Field(min_length=1, max_length=100)]
Status = Literal["wanting", "reading", "finished"]

@mcp.resource("bookmarks://user/")
async def get_user_books():
    """Full reading list for a user."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_user_books(user_id=USER_ID)


@mcp.resource("bookmarks://user//{status}")
async def get_user_books_by_status(status: Status):
    """User's books filtered by status: wanting, reading, or finished."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_user_books(user_id=USER_ID, status=status)
