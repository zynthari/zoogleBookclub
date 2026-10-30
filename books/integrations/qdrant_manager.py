from qdrant_client import QdrantClient
from django.conf import settings
from qdrant_client.models import Distance, VectorParams, PointStruct


class ColectionDoesNotExists(Exception):
    def __init__(self, collection_name):
        self.collection_name = collection_name

    def __str__(self):
        return f"Коллекция '{self.collection_name}' не существует"


class CollectionAlreadyExists(Exception):
    def __init__(self, collection_name):
        self.collection_name = collection_name
    def __str__(self):
        return f"Коллекция с именем '{self.collection_name}' уже существует"

class QdrantManager:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)

    def check_collection_exists(self, collection_name):
        if not self.client.collection_exists(collection_name):
            raise ColectionDoesNotExists(collection_name)
        return

    def create_collection(self, size, collection_name="sample_collection", distance=Distance.COSINE):
        if self.client.collection_exists(collection_name):
            raise CollectionAlreadyExists(collection_name)

        print(f"Создание коллекции '{collection_name}'...")

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=size,
                distance=distance,
            ),
        )

        print(f"Коллекция '{collection_name}' успешно создана")


    def upsert_into_collection(self, collection_name, item_data):
        self.check_collection_exists(collection_name)

        # формируем точки для ВБД
        points = []
        for item in item_data:
            points.append(
                PointStruct(
                    id=item["id"],
                    vector=item["vector"],
                    payload=item["meta"]
                )
            )

        self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )

    def search_similar_data(self, collection_name, query_vector, limit=5):
        self.check_collection_exists(collection_name)

        search_result = self.client.query_points(
            collection_name=collection_name, query=query_vector, limit=limit
        )

        # пока сериализую тут
        result = {}
        for i, item in enumerate(search_result.points):
            result[i] = item.payload

        return result

    def delete_collection(self, collection_name):
        self.client.delete_collection(collection_name=collection_name)

    def get_collection_count(self, collection_name):
        return self.client.count(
            collection_name=collection_name,
            exact=True # нужен точный подсчет
        ).count