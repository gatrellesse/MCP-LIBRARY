from app.mcp.server import mcp
from app.db.qdrant import BookQdrant


@mcp.tool()
def add_bookmark(user_id: str, title: str, status: str = "wanting"):
    """Mark a library book as owned/tracked by a user. Status: 'wanting', 'reading', or 'finished'."""
    with BookQdrant() as qdrant:
        found = qdrant.add_bookmark(user_id=user_id, title=title, status=status)
    if not found:
        raise ValueError(f"Book '{title}' not found in the library.")
    return f"Book '{title}' added to your list with status '{status}'."


@mcp.tool()
def delete_bookmark(user_id: str, title: str):
    """Remove a book from the user's reading list."""
    with BookQdrant() as qdrant:
        found = qdrant.delete_bookmark(user_id=user_id, title=title)
    if not found:
        raise ValueError(f"No bookmark found for '{title}'.")
    return f"Book '{title}' removed from your list."


@mcp.tool()
def update_book_status(user_id: str, title: str, new_status: str):
    """Update the reading status of a bookmarked book. Status: 'wanting', 'reading', or 'finished'."""
    with BookQdrant() as qdrant:
        found = qdrant.update_status(user_id=user_id, title=title, status=new_status)
    if not found:
        raise ValueError(f"No bookmark found for '{title}'.")
    return f"'{title}' status updated to '{new_status}'."


@mcp.tool()
def list_user_books(user_id: str, status: str | None = None):
    """List all books in the user's reading list, optionally filtered by status."""
    with BookQdrant() as qdrant:
        return qdrant.list_user_books(user_id=user_id, status=status)


@mcp.tool()
def search_user_books(user_id: str, query: str, status: str | None = None):
    """Semantic search within the user's bookmarked books."""
    with BookQdrant() as qdrant:
        return qdrant.search_user_books(query=query, user_id=user_id, status=status)
