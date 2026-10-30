from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from django.conf import settings
import json
from qdrant_client.models import PointStruct

from books.integrations import QdrantManager
from books.integrations.Embeddings import SentenceTransformerManager, BadEmbeddingModel
from books.integrations.Embeddings.ollama_manager import OllamaManager
from books.service.enrich_book_with_id import enrich_book_with_id
from books.service.validate_json_file import validate_json_file

def get_rid_of_doubles(data):
    # вытащим уникальные ключи
    ids = set()
    undoubled_data = {}
    for item in data:
        if item["id"] not in ids:
            ids.add(item["id"])
            undoubled_data[item["id"]] = item
        else:
            # оставляю дубль с более длинным описанием
            if len(item["meta"]["description"]) > len(undoubled_data[item["id"]]["meta"]["description"]):
                undoubled_data[item["id"]] = item

    return list(undoubled_data.values())



def enrich_book_collection(collection_name, json_file):
    books = validate_json_file(json_file)

    match settings.EMBEDDING_MODE:
        case "SentenceTransformer":
            embedding_manager = SentenceTransformerManager()
        case "Ollama":
            embedding_manager = OllamaManager()
        case _:
            raise BadEmbeddingModel

    qm = QdrantManager()

    book_data = get_rid_of_doubles([{"id": enrich_book_with_id(book), "meta": book} for book in books])

    if len(book_data) == 0:
        return 0

    # и вот тут все же можно батчом составить вектора
    book_vectors = embedding_manager.encode_batch([book["meta"]["description"] for book in book_data])

    # дополняем
    for data, vector in zip(book_data, book_vectors, strict=True):
        data["vector"] = vector

    qm.upsert_into_collection(
        collection_name=collection_name,
        item_data=book_data,
    )

    # плохая метрика на самом деле
    return len(book_data)

