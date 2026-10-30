from django.conf import settings

from books.integrations.Embeddings import SentenceTransformerManager, BadEmbeddingModel
from books.integrations.Embeddings.ollama_manager import OllamaManager


def get_dimension() -> int:
    """
    Возвращает размерность модели, выбранной в EMBEDDING_MODE.
    """
    match settings.EMBEDDING_MODE:
        case "SentenceTransformer":
            model = SentenceTransformerManager()
        case "Ollama":
            model = OllamaManager()
        case _:
            raise BadEmbeddingModel(f"Неизвестный embedding-провайдер: {settings.EMBEDDING_MODE}")

    return len(model.encode("Определение размерности embedding-модели"))
