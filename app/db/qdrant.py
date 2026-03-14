import os
from uuid import uuid4

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    HasIdCondition,
    MatchValue,
    NamedVector,
    PayloadSchemaType,
    PointStruct,
    UpdateStatus,
    VectorParams,
)

from app.embeddings import Embedder, VECTOR_SIZE


SYNOPSIS_VECTOR = "synopsis"
TEXT_VECTOR = "text"  # reserved for future book text embeddings

LIBRARY = "library"      # shared catalog of all books
BOOKMARKS = "bookmarks"  # user-owned reading markers


class BookQdrant:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = AsyncQdrantClient(host=host, port=port, api_key=os.getenv("QDRANT__SERVICE__API_KEY"), https=False)
        self.embedder = Embedder()

    async def __aenter__(self):
        await self._ensure_collections()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    async def _ensure_collections(self):
        existing = {c.name for c in (await self.client.get_collections()).collections}

        if LIBRARY not in existing:
            await self.client.create_collection(
                collection_name=LIBRARY,
                vectors_config={
                    SYNOPSIS_VECTOR: VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                    # TEXT_VECTOR: VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                },
            )
            for field in ["title", "author", "genre"]:
                await self.client.create_payload_index(
                    collection_name=LIBRARY,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD,
                )

        if BOOKMARKS not in existing:
            await self.client.create_collection(
                collection_name=BOOKMARKS,
                vectors_config={},  # payload-only, no vector search needed
            )
            for field in ["user_id", "book_id", "title", "status"]:
                await self.client.create_payload_index(
                    collection_name=BOOKMARKS,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD,
                )

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    async def _resolve_library_id(self, title: str) -> str | None:
        results, _ = await self.client.scroll(
            collection_name=LIBRARY,
            scroll_filter=Filter(must=[
                FieldCondition(key="title", match=MatchValue(value=title)),
            ]),
            with_payload=False,
            limit=1,
        )
        return str(results[0].id) if results else None

    async def _resolve_bookmark_id(self, user_id: str, title: str) -> str | None:
        results, _ = await self.client.scroll(
            collection_name=BOOKMARKS,
            scroll_filter=Filter(must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="title", match=MatchValue(value=title)),
            ]),
            with_payload=False,
            limit=1,
        )
        return str(results[0].id) if results else None

    # -------------------------------------------------------------------------
    # Library — shared book catalog
    # -------------------------------------------------------------------------

    async def add_to_library(self, title: str, author: str, genre: str, synopsis: str) -> str | None:
        """Add a book to the shared library. Returns the book_id, or None if title already exists."""
        if await self._resolve_library_id(title) is not None:
            return None
        book_id = str(uuid4())
        result = await self.client.upsert(
            collection_name=LIBRARY,
            points=[
                PointStruct(
                    id=book_id,
                    vector={SYNOPSIS_VECTOR: self.embedder.embed(synopsis)},
                    payload={
                        "title": title,
                        "author": author,
                        "genre": genre,
                        "synopsis": synopsis,
                        "has_text_embedding": False,
                    },
                )
            ],
        )
        if result.status not in (UpdateStatus.ACKNOWLEDGED, UpdateStatus.COMPLETED):
            return None
        
        return book_id

    async def get_book(self, title: str) -> dict | None:
        """Retrieve a book from the library by title."""
        book_id = await self._resolve_library_id(title)
        if book_id is None:
            return None
        results = await self.client.retrieve(
            collection_name=LIBRARY,
            ids=[book_id],
            with_payload=True,
        )
        if not results:
            return None
        r = results[0]
        return {"id": r.id, **r.payload}

    async def search_library(
        self,
        query: str,
        author: str | None = None,
        genre: str | None = None,
        limit: int = 5,
    ) -> list[dict]:
        """Semantic search across the entire library."""
        must_conditions = []
        for field, value in [("author", author), ("genre", genre)]:
            if value:
                must_conditions.append(FieldCondition(key=field, match=MatchValue(value=value)))

        results = await self.client.query(
            collection_name=LIBRARY,
            query_text=NamedVector(name=SYNOPSIS_VECTOR, vector=self.embedder.embed(query)),
            query_filter=Filter(must=must_conditions) if must_conditions else None,
            limit=limit,
            with_payload=True,
        )
        return [{"id": r.id, "score": r.score, **r.payload} for r in results]

    async def list_all_books(self) -> list[dict]:
        """Return all books in the library."""
        results, _ = await self.client.scroll(
            collection_name=LIBRARY,
            with_payload=True,
            limit=1000,
        )
        return [{"id": r.id, **r.payload} for r in results]

    async def list_genres(self) -> list[str]:
        """Return all distinct genres in the library."""
        results, _ = await self.client.scroll(
            collection_name=LIBRARY,
            with_payload=["genre"],
            limit=1000,
        )
        return sorted({r.payload["genre"] for r in results if r.payload.get("genre")})

    async def list_authors(self) -> list[str]:
        """Return all distinct authors in the library."""
        results, _ = await self.client.scroll(
            collection_name=LIBRARY,
            with_payload=["author"],
            limit=1000,
        )
        return sorted({r.payload["author"] for r in results if r.payload.get("author")})

    async def delete_from_library(self, title: str) -> bool:
        """Remove a book from the library and cascade-delete all user bookmarks for it."""
        book_id = await self._resolve_library_id(title)
        if book_id is None:
            return False
        await self.client.delete(collection_name=LIBRARY, points_selector=[book_id])
        await self.client.delete(
            collection_name=BOOKMARKS,
            points_selector=Filter(must=[
                FieldCondition(key="book_id", match=MatchValue(value=book_id)),
            ]),
        )
        return True

    async def update_text_embedding(self, title: str, text: str) -> bool:
        """Embed and store the full book text. Call once TEXT_VECTOR is enabled in the collection."""
        book_id = await self._resolve_library_id(title)
        if book_id is None:
            return False
        await self.client.update_vectors(
            collection_name=LIBRARY,
            points=[PointStruct(id=book_id, vector={TEXT_VECTOR: self.embedder.embed(text)})],
        )
        await self.client.set_payload(
            collection_name=LIBRARY,
            payload={"has_text_embedding": True},
            points=[book_id],
        )
        return True

    # -------------------------------------------------------------------------
    # Bookmarks — user reading list
    # -------------------------------------------------------------------------

    async def add_bookmark(self, user_id: str, title: str, status: str = "wanting") -> bool:
        """Mark a library book as owned/tracked by a user."""
        book_id = await self._resolve_library_id(title)
        if book_id is None:
            return False
        await self.client.upsert(
            collection_name=BOOKMARKS,
            points=[
                PointStruct(
                    id=str(uuid4()),
                    vector={},
                    payload={
                        "user_id": user_id,
                        "book_id": book_id,
                        "title": title,  # denormalized for fast lookup
                        "status": status,
                    },
                )
            ],
        )
        return True

    async def update_status(self, user_id: str, title: str, status: str) -> bool:
        """Update the reading status of a user's bookmark."""
        bookmark_id = await self._resolve_bookmark_id(user_id, title)
        if bookmark_id is None:
            return False
        await self.client.set_payload(
            collection_name=BOOKMARKS,
            payload={"status": status},
            points=[bookmark_id],
        )
        return True

    async def delete_bookmark(self, user_id: str, title: str) -> bool:
        """Remove a user's bookmark."""
        bookmark_id = await self._resolve_bookmark_id(user_id, title)
        if bookmark_id is None:
            return False
        await self.client.delete(collection_name=BOOKMARKS, points_selector=[bookmark_id])
        return True

    async def list_user_books(self, user_id: str, status: str | None = None) -> list[dict]:
        """List all bookmarks for a user, optionally filtered by status."""
        must_conditions = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        if status:
            must_conditions.append(FieldCondition(key="status", match=MatchValue(value=status)))

        results, _ = await self.client.scroll(
            collection_name=BOOKMARKS,
            scroll_filter=Filter(must=must_conditions),
            with_payload=True,
            limit=100,
        )
        return [{"id": r.id, **r.payload} for r in results]

    async def search_user_books(
        self,
        query: str,
        user_id: str,
        status: str | None = None,
        limit: int = 5,
    ) -> list[dict]:
        """Semantic search restricted to a user's bookmarked books."""
        must_conditions = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        if status:
            must_conditions.append(FieldCondition(key="status", match=MatchValue(value=status)))

        bookmarks, _ = await self.client.scroll(
            collection_name=BOOKMARKS,
            scroll_filter=Filter(must=must_conditions),
            with_payload=True,
            limit=1000,
        )
        if not bookmarks:
            return []

        book_ids = [b.payload["book_id"] for b in bookmarks]
        book_id_to_status = {b.payload["book_id"]: b.payload["status"] for b in bookmarks}

        results = await self.client.query(
            collection_name=LIBRARY,
            query_text=NamedVector(name=SYNOPSIS_VECTOR, vector=self.embedder.embed(query)),
            query_filter=Filter(must=[HasIdCondition(has_id=book_ids)]),
            limit=limit,
            with_payload=True,
        )
        return [
            {"id": r.id, "score": r.score, "status": book_id_to_status.get(str(r.id)), **r.payload}
            for r in results
        ]
