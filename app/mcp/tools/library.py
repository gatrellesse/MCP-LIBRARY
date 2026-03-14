from app.mcp.server import mcp
from app.db.qdrant import BookQdrant


@mcp.tool()
async def add_book(title: str, author: str, genre: str, synopsis: str):
    """Add a new book to the shared library."""
    async with BookQdrant() as qdrant:
        book_id = await qdrant.add_to_library(title=title, author=author, genre=genre, synopsis=synopsis)
    if book_id is None:
        raise ValueError(f"Failed to add '{title}' to the library.")
    return f"Book '{title}' by {author} added to the library."

@mcp.tool()
async def delete_book(title: str):
    """Remove a book from the shared library."""
    async with BookQdrant() as qdrant:
        found = await qdrant.delete_from_library(title=title)
    if not found:
        raise ValueError(f"Book '{title}' not found in the library.")
    return f"Book '{title}' removed from the library."

@mcp.tool()
async def get_book(title: str):
    """Get details of a book from the library."""
    async with BookQdrant() as qdrant:
        book = await qdrant.get_book(title=title)
    if book is None:
        raise ValueError(f"Book '{title}' not found in the library.")
    return book


@mcp.tool()
async def search_library(query: str, author: str | None = None, genre: str | None = None):
    """Semantic search across the entire library."""
    async with BookQdrant() as qdrant:
        return await qdrant.search_library(query=query, author=author, genre=genre)
