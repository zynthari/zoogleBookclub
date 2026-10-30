from sentence_transformers import SentenceTransformer

from books.integrations.Embeddings.base import BaseEmbeddingModel


class SentenceTransformerManager(BaseEmbeddingModel):
    def __init__(self):
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        super().__init__()

    def encode(self, text: str):
        return self.model.encode(text)

    def encode_batch(self, texts: list[str]):
        return self.model.encode(texts).tolist()
