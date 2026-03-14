from app.mcp.server import mcp
from app.db.qdrant import BookQdrant


@mcp.resource("library://books")
async def get_all_books():
    """Full catalog of all books available in the library."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_all_books()


@mcp.resource("library://books/{title}")
async def get_book(title: str):
    """Details of a single book from the library."""
    async with BookQdrant() as qdrant:
        return await qdrant.get_book(title=title)


@mcp.resource("library://genres")
async def get_genres():
    """All distinct genres available in the library."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_genres()


@mcp.resource("library://authors")
async def get_authors():
    """All distinct authors available in the library."""
    async with BookQdrant() as qdrant:
        return await qdrant.list_authors()
