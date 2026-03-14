from app.mcp.server import mcp
from app.db.qdrant import BookQdrant


@mcp.resource("bookmarks://user/{user_id}")
async def get_user_books(user_id: str):
    """Full reading list for a user."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_user_books(user_id=user_id)


@mcp.resource("bookmarks://user/{user_id}/{status}")
async def get_user_books_by_status(user_id: str, status: str):
    """User's books filtered by status: wanting, reading, or finished."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_user_books(user_id=user_id, status=status)
