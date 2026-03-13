from app.mcp.server import mcp
from app.db.qdrant import BookQdrant


@mcp.resource("library://books")
def get_all_books():
    """Full catalog of all books available in the library."""
    with BookQdrant() as qdrant:
        return qdrant.list_all_books()


@mcp.resource("library://books/{title}")
def get_book(title: str):
    """Details of a single book from the library."""
    with BookQdrant() as qdrant:
        return qdrant.get_book(title=title)


@mcp.resource("library://genres")
def get_genres():
    """All distinct genres available in the library."""
    with BookQdrant() as qdrant:
        return qdrant.list_genres()


@mcp.resource("library://authors")
def get_authors():
    """All distinct authors available in the library."""
    with BookQdrant() as qdrant:
        return qdrant.list_authors()
