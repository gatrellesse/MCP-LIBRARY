from typing import Annotated

from pydantic import Field

from app.mcp.server import mcp
from app.db.qdrant import BookQdrant

Title  = Annotated[str, Field(min_length=1, max_length=300)]
Author = Annotated[str, Field(min_length=1, max_length=200)]
Genre  = Annotated[str, Field(min_length=1, max_length=100)]


@mcp.tool()
async def add_book(
    title: Title,
    author: Author,
    genre: Genre,
    synopsis: Annotated[str, Field(min_length=1, max_length=5000)],
):
    """Add a new book to the shared library."""
    async with BookQdrant() as qdrant:
        book_id = await qdrant.add_to_library(title=title, author=author, genre=genre, synopsis=synopsis)
    if book_id is None:
        raise ValueError(f"Failed to add '{title}' to the library.")
    return f"Book '{title}' by {author} added to the library."


@mcp.tool()
async def delete_book(title: Title):
    """Remove a book from the shared library."""
    async with BookQdrant() as qdrant:
        found = await qdrant.delete_from_library(title=title)
    if not found:
        raise ValueError(f"Book '{title}' not found in the library.")
    return f"Book '{title}' removed from the library."


@mcp.tool()
async def get_book(title: Title):
    """Get details of a book from the library."""
    async with BookQdrant() as qdrant:
        book = await qdrant.get_book(title=title)
    if book is None:
        raise ValueError(f"Book '{title}' not found in the library.")
    return book


@mcp.tool()
async def search_library(
    query: Annotated[str, Field(min_length=1, max_length=1000)],
    author: Author | None = None,
    genre: Genre | None = None,
):
    """Semantic search across the entire library."""
    async with BookQdrant() as qdrant:
        return await qdrant.search_library(query=query, author=author, genre=genre)
