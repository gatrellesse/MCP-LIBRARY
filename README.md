# book-mcp

An MCP (Model Context Protocol) server for managing and semantically searching your personal book collection.

Instead of keyword search, book-mcp uses vector embeddings to find books by *meaning* — search for "a story about redemption in space" and get relevant results even if those words don't appear in the synopsis.

## Features

- Add books with metadata (title, author, genre, synopsis, status)
- Semantic search across your library using natural language
- Filter by author, genre, or reading status (`wanting` / `reading` / `finished`)
- Per-user book collections
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

# 4. Run the MCP server
python main.py
```

## Add to Claude Code

```bash
claude mcp add --transport stdio book-mcp -- uv run python /path/to/book-mcp/main.py
```

## Project Structure

```
book-mcp/
├── main.py                        # Entry point — starts the MCP server
├── pyproject.toml
├── docker-compose.yml             # Qdrant service
└── app/
    ├── embeddings.py              # FastEmbed wrapper
    ├── db/
    │   └── qdrant.py              # BookQdrant — vector DB interface
    └── mcp/
        ├── server.py              # MCP server definition
        ├── tools/                 # MCP tools (add, search, update, delete)
        ├── resources/             # MCP resources (library, bookmarks)
        └── prompts/               # MCP prompts
```

## Book Status Values

| Status | Meaning |
|--------|---------|
| `wanting` | On your wishlist |
| `reading` | Currently reading |
| `finished` | Done |
