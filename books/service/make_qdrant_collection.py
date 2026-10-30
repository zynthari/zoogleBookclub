from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from books.service.get_dimension import get_dimension


def make_qdrant_collection(collection_name = "sample_collection"):
    size = get_dimension()
    # подключаемся к Qdrant
    client = QdrantClient(url=settings.QDRANT_URL,)

    if client.collection_exists(collection_name):
        print(f"Коллекция '{collection_name}' уже существует")
        return

    print(f"Создание коллекции '{collection_name}'...")

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=get_dimension(),
            distance=Distance.COSINE,  # Метрика расстояния
        ),
    )

    print(f"Коллекция '{collection_name}' успешно создана")
