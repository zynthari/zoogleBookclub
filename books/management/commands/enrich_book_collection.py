from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from books.service.enrich_book_collection import enrich_book_collection


class Command(BaseCommand):
    help = "Наполнение коллекции книгами из json-файла"

    def add_arguments(self, parser):
        parser.add_argument("--file", default="task/books.json")
        parser.add_argument("--collection", default="sample_collection")

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.is_absolute():
            path = settings.BASE_DIR / path
        try:
            count = enrich_book_collection(collection_name=options["collection"], json_file=path)
        except (OSError, ValueError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f"Обработано книг: {count}."))
