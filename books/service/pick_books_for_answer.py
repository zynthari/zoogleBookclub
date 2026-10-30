from django.conf import settings

from books.integrations import QdrantManager
from books.integrations.Embeddings import SentenceTransformerManager
from books.integrations.Embeddings.exceptions import BadEmbeddingModel
from books.integrations.Embeddings.ollama_manager import OllamaManager
from books.integrations.LLM import LLMManager


def pick_books_for_answer(question):
    match settings.EMBEDDING_MODE:
        case "SentenceTransformer":
            emb_manager = SentenceTransformerManager()
        case "Ollama":
            emb_manager = OllamaManager()
        case _:
            raise BadEmbeddingModel

    qm = QdrantManager()

    # делаем вектор из вопроса
    question_vector = emb_manager.encode(question)

    # ищем 5 наиболее похожих книг
    search_result = qm.search_similar_data(
        collection_name="sample_collection", query_vector=question_vector, limit=5
    )

    llm_manager = LLMManager()

    return llm_manager.generate_recommendation(question=question, answer=search_result)
