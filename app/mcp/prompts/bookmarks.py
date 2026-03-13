from app.mcp.server import mcp


@mcp.prompt()
def books_by_status(user_id: str, status: str) -> str:
    """List books for a user filtered by reading status (wanting/reading/finished)."""
    return (
        f"List all books for user '{user_id}' with status '{status}'. "
        f"Use the bookmarks://user/{user_id}/{status} resource."
    )


@mcp.prompt()
def current_reading(user_id: str) -> str:
    """Show what the user is currently reading."""
    return (
        f"Show what user '{user_id}' is currently reading. "
        f"Use the bookmarks://user/{user_id}/reading resource."
    )


@mcp.prompt()
def reading_wishlist(user_id: str) -> str:
    """Show the user's reading wishlist (wanting status)."""
    return (
        f"Show the reading wishlist for user '{user_id}'. "
        f"Use the bookmarks://user/{user_id}/wanting resource."
    )
