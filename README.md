# book-mcp

An MCP (Model Context Protocol) server for managing and semantically searching a book library.

The idea is simple: there is one **shared library** containing all available books. Each user then maintains their own **bookmark list** — a personal reading list drawn from that library, with a status (`wanting`, `reading`, or `finished`) attached to each entry.

The shared library is currently populated manually and can be expanded over time as new books are added.

Instead of keyword search, book-mcp uses vector embeddings to find books by *meaning* — search for "a story about redemption in space" and get relevant results even if those words don't appear in the synopsis.

## Features

- Add books with metadata (title, author, genre, synopsis, status)
- Semantic search across the library using natural language
- Filter by author, genre, or reading status (`wanting` / `reading` / `finished`)
- Per-user book collections with token-based authentication
- MCP tools, resources, and prompts for AI assistant integration

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Package manager | uv |
| Vector DB | Qdrant (via Docker) |
| Embeddings | FastEmbed (`BAAI/bge-small-en-v1.5`, 384-dim) |
| Protocol | MCP (Model Context Protocol) |

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker & Docker Compose

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/your-username/book-mcp.git
cd book-mcp

# 2. Start Qdrant
docker-compose up -d

# 3. Install dependencies
uv pip install -e .
```

## User Management

The server uses token-based auth. Each user gets a token stored in `.env.library` on the server side.

```bash
# Add a user and generate their token
uv run python manage_tokens.py add <user_id>

# List all users and tokens
uv run python manage_tokens.py list

# Revoke a user
uv run python manage_tokens.py revoke <user_id>
```

## Add to Claude Code

Each user sets their token in `.env`:

```ini
USER_TOKEN=<your-token>
```

Then reference it in `.mcp.json`:

```json
{
  "mcpServers": {
    "book-mcp": {
      "command": "uv",
      "args": ["--directory", "~/book-mcp", "run", "python", "main.py"]
    }
  }
}
```

Or via the CLI:

```bash
claude mcp add --transport stdio book-mcp -- uv run --directory ~/book-mcp python main.py
```

## Project Structure

```
book-mcp/
├── main.py                        # Entry point — starts the MCP server
├── manage_tokens.py               # CLI for managing user tokens
├── pyproject.toml
├── docker-compose.yml             # Qdrant service
└── app/
    ├── embeddings.py              # FastEmbed wrapper
    ├── db/
    │   └── qdrant.py              # BookQdrant — vector DB interface
    └── mcp/
        ├── server.py              # MCP server definition + auth
        ├── tools/                 # MCP tools (add, search, update, delete, bookmarks)
        ├── resources/             # MCP resources (library, bookmarks)
        └── prompts/               # MCP prompts
```

## Examples

Once connected, you can talk to Claude naturally:

**Search the library**
> "Find me a fantasy book about a chosen hero with political intrigue"

**Add a book to the library**
> "Add The Name of the Wind by Patrick Rothfuss — it's fantasy, and the synopsis is: a legendary wizard recounts his life story to a chronicler"

**Bookmark a book**
> "Add The Hobbit to my reading list"
> "Mark A Game of Thrones as currently reading"

**Search your own books**
> "Which books on my list are about war or conflict?"

**Update status**
> "I finished The Hobbit, mark it as done"

**Remove a bookmark**
> "Remove The Way of Kings from my list"

