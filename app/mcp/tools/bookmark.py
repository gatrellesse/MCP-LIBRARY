import logging
from typing import Annotated, Literal

from pydantic import Field

from app.mcp.server import mcp
from app.db.qdrant import BookQdrant

logger = logging.getLogger(__name__)

Status = Literal["wanting", "reading", "finished"]
UserId = Annotated[str, Field(min_length=1, max_length=100)]
Title  = Annotated[str, Field(min_length=1, max_length=300)]


@mcp.tool()
async def add_bookmark(user_id: UserId, title: Title, status: Status = "wanting"):
    """Mark a library book as owned/tracked by a user."""
    logger.info("add_bookmark: user_id=%r title=%r status=%r", user_id, title, status)
    async with BookQdrant() as qdrant:
        found = await qdrant.add_bookmark(user_id=user_id, title=title, status=status)
    if not found:
        logger.warning("add_bookmark: book not found title=%r", title)
        raise ValueError(f"Book '{title}' not found in the library.")
    return f"Book '{title}' added to your list with status '{status}'."


@mcp.tool()
async def delete_bookmark(user_id: UserId, title: Title):
    """Remove a book from the user's reading list."""
    logger.info("delete_bookmark: user_id=%r title=%r", user_id, title)
    async with BookQdrant() as qdrant:
        found = await qdrant.delete_bookmark(user_id=user_id, title=title)
    if not found:
        logger.warning("delete_bookmark: not found user_id=%r title=%r", user_id, title)
        raise ValueError(f"No bookmark found for '{title}'.")
    return f"Book '{title}' removed from your list."


@mcp.tool()
async def update_book_status(user_id: UserId, title: Title, new_status: Status):
    """Update the reading status of a bookmarked book."""
    logger.info("update_book_status: user_id=%r title=%r new_status=%r", user_id, title, new_status)
    async with BookQdrant() as qdrant:
        found = await qdrant.update_status(user_id=user_id, title=title, status=new_status)
    if not found:
        logger.warning("update_book_status: not found user_id=%r title=%r", user_id, title)
        raise ValueError(f"No bookmark found for '{title}'.")
    return f"'{title}' status updated to '{new_status}'."


@mcp.tool()
async def list_user_books(user_id: UserId, status: Status | None = None):
    """List all books in the user's reading list, optionally filtered by status."""
    logger.info("list_user_books: user_id=%r status=%r", user_id, status)
    async with BookQdrant() as qdrant:
        return await qdrant.list_user_books(user_id=user_id, status=status)


@mcp.tool()
async def search_user_books(
    user_id: UserId,
    query: Annotated[str, Field(min_length=1, max_length=1000)],
    status: Status | None = None,
):
    """Semantic search within the user's bookmarked books."""
    logger.info("search_user_books: user_id=%r query=%r status=%r", user_id, query, status)
    async with BookQdrant() as qdrant:
        results = await qdrant.search_user_books(query=query, user_id=user_id, status=status)
    logger.info("search_user_books: returned %d results", len(results))
    return results
