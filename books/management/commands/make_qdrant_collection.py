from django.core.management import BaseCommand

from books.integrations import QdrantManager
from books.service.get_dimension import get_dimension


class Command(BaseCommand):
    help = "Инициализация коллекции в Qdrant"

    def add_arguments(self, parser):
        parser.add_argument("--collection", default="sample_collection")

    def handle(self, *args, **options):
        collection_name = options["collection"]

        qm = QdrantManager()
        if qm.client.collection_exists(collection_name):
            self.stdout.write(f"Коллекция {collection_name} уже существует; данные сохранены.")
            return
        qm.create_collection(collection_name=collection_name, size=get_dimension())

        self.stdout.write(f"Коллекция {collection_name} создана, ждем ее наполнения!")
