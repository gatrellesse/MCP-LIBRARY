from app.mcp.server import mcp
from app.db.qdrant import BookQdrant


@mcp.tool()
async def add_bookmark(user_id: str, title: str, status: str = "wanting"):
    """Mark a library book as owned/tracked by a user. Status: 'wanting', 'reading', or 'finished'."""
    async with BookQdrant() as qdrant:
        found = await qdrant.add_bookmark(user_id=user_id, title=title, status=status)
    if not found:
        raise ValueError(f"Book '{title}' not found in the library.")
    return f"Book '{title}' added to your list with status '{status}'."


@mcp.tool()
async def delete_bookmark(user_id: str, title: str):
    """Remove a book from the user's reading list."""
    async with BookQdrant() as qdrant:
        found = await qdrant.delete_bookmark(user_id=user_id, title=title)
    if not found:
        raise ValueError(f"No bookmark found for '{title}'.")
    return f"Book '{title}' removed from your list."


@mcp.tool()
async def update_book_status(user_id: str, title: str, new_status: str):
    """Update the reading status of a bookmarked book. Status: 'wanting', 'reading', or 'finished'."""
    async with BookQdrant() as qdrant:
        found = await qdrant.update_status(user_id=user_id, title=title, status=new_status)
    if not found:
        raise ValueError(f"No bookmark found for '{title}'.")
    return f"'{title}' status updated to '{new_status}'."


@mcp.tool()
async def list_user_books(user_id: str, status: str | None = None):
    """List all books in the user's reading list, optionally filtered by status."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_user_books(user_id=user_id, status=status)


@mcp.tool()
async def search_user_books(user_id: str, query: str, status: str | None = None):
    """Semantic search within the user's bookmarked books."""
    async with BookQdrant() as qdrant:
        return await qdrant.search_user_books(query=query, user_id=user_id, status=status)
