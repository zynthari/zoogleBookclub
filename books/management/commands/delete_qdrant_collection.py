from django.core.management import BaseCommand

from books.integrations import QdrantManager


class Command(BaseCommand):
    help = "Удаление коллекции в Qdrant"

    def handle(self, *args, **options):
        collection_name = input("Какую коллекцию удалить? ")

        qm = QdrantManager()
        qm.delete_collection(collection_name)

        self.stdout.write(f"Коллекция {collection_name} удалена :c")