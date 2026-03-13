from fastembed import TextEmbedding


EMBED_MODEL = "BAAI/bge-small-en-v1.5"
VECTOR_SIZE = 384


class Embedder:
    def __init__(self):
        self._model = TextEmbedding(model_name=EMBED_MODEL)

    def embed(self, text: str) -> list[float]:
        return list(next(iter(self._model.embed([text]))))