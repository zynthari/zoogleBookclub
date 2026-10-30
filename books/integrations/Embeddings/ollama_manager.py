from openai import OpenAI

from django.conf import settings

from books.integrations.Embeddings.base import BaseEmbeddingModel


class OllamaManager(BaseEmbeddingModel):
    def __init__(self):
        self.client = OpenAI(base_url=settings.OLLAMA_BASE_URL, api_key="ollama")
        self.model = settings.OLLAMA_EMBEDDING_MODEL
        super().__init__()

    def encode(self, query):
        response = self.client.embeddings.create(model=self.model, input=query)
        return response.data[0].embedding

    def encode_batch(self, texts: list[str]):
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in sorted(response.data, key=lambda item: item.index)]
