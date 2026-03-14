import logging
from typing import Annotated

from pydantic import Field

from app.mcp.server import mcp
from app.db.qdrant import BookQdrant

logger = logging.getLogger(__name__)

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
    logger.info("add_book: title=%r author=%r genre=%r", title, author, genre)
    async with BookQdrant() as qdrant:
        book_id = await qdrant.add_to_library(title=title, author=author, genre=genre, synopsis=synopsis)
    if book_id is None:
        logger.warning("add_book duplicate: title=%r", title)
        raise ValueError(f"'{title}' already exists in the library.")
    logger.info("add_book succeeded: book_id=%s", book_id)
    return f"Book '{title}' by {author} added to the library."


@mcp.tool()
async def delete_book(title: Title):
    """Remove a book from the shared library."""
    logger.info("delete_book: title=%r", title)
    async with BookQdrant() as qdrant:
        found = await qdrant.delete_from_library(title=title)
    if not found:
        logger.warning("delete_book: not found title=%r", title)
        raise ValueError(f"Book '{title}' not found in the library.")
    return f"Book '{title}' removed from the library."


@mcp.tool()
async def get_book(title: Title):
    """Get details of a book from the library."""
    logger.info("get_book: title=%r", title)
    async with BookQdrant() as qdrant:
        book = await qdrant.get_book(title=title)
    if book is None:
        logger.warning("get_book: not found title=%r", title)
        raise ValueError(f"Book '{title}' not found in the library.")
    return book


@mcp.tool()
async def search_library(
    query: Annotated[str, Field(min_length=1, max_length=1000)],
    author: Author | None = None,
    genre: Genre | None = None,
):
    """Semantic search across the entire library."""
    logger.info("search_library: query=%r author=%r genre=%r", query, author, genre)
    async with BookQdrant() as qdrant:
        results = await qdrant.search_library(query=query, author=author, genre=genre)
    logger.info("search_library: returned %d results", len(results))
    return results
