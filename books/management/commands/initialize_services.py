import json
from time import monotonic, sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command
from qdrant_client.models import Distance

from books.integrations import QdrantManager
from books.service.get_dimension import get_dimension


class Command(BaseCommand):
    help = "Ожидание сервисов, загрузка embedding-модели и подготовка коллекции"

    def add_arguments(self, parser):
        parser.add_argument("--collection", default="sample_collection")
        parser.add_argument("--wait-timeout", type=int, default=120)
        parser.add_argument("--pull-timeout", type=int, default=1800)

    def wait_for_service(self, name, url, timeout):
        self.stdout.write(f"Ожидаем {name}...")
        deadline = monotonic() + timeout
        last_error = None
        while monotonic() < deadline:
            try:
                with urlopen(Request(url), timeout=5):
                    return
            except (URLError, OSError) as exc:
                last_error = exc
                sleep(1)
        raise CommandError(f"{name} не готов за {timeout} секунд: {last_error}")

    def ensure_model(self, base_url, timeout):
        model = settings.OLLAMA_EMBEDDING_MODEL
        data = json.dumps({"model": model}).encode()
        request = Request(
            f"{base_url}/api/show", data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=30):
                self.stdout.write(f"Модель {model} уже скачана.")
                return
        except HTTPError as exc:
            if exc.code != 404:
                raise

        self.stdout.write(f"Скачиваем {model}; первая загрузка может занять несколько минут...")
        self.stdout.flush()
        request = Request(
            f"{base_url}/api/pull",
            data=json.dumps({"model": model, "stream": False}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=timeout) as response:
            result = json.load(response)
        if result.get("error"):
            raise CommandError(f"Не удалось скачать {model}: {result['error']}")
        if result.get("status") != "success":
            raise CommandError(f"Ollama не подтвердила завершение загрузки {model}.")
        self.stdout.write(f"Модель {model} скачана.")

    def ensure_collection(self, collection_name):
        size = get_dimension()
        if size <= 0:
            raise CommandError("Embedding-модель вернула пустой вектор.")
        manager = QdrantManager()
        if manager.client.collection_exists(collection_name):
            vectors = manager.client.get_collection(collection_name).config.params.vectors
            if getattr(vectors, "size", None) != size or getattr(vectors, "distance", None) != Distance.COSINE:
                raise CommandError(
                    f"Коллекция {collection_name} несовместима с выбранной моделью "
                    f"(ожидается размерность {size}, метрика Cosine). Данные не изменены."
                )
            self.stdout.write(f"Коллекция {collection_name} уже существует; данные сохранены.")
        else:
            manager.create_collection(collection_name=collection_name, size=size)

    def handle(self, *args, **options):
        if options["wait_timeout"] <= 0 or options["pull_timeout"] <= 0:
            raise CommandError("Таймауты должны быть положительными числами.")
        try:
            self.wait_for_service(
                "Qdrant", f"{settings.QDRANT_URL.rstrip('/')}/readyz", options["wait_timeout"]
            )
            if settings.EMBEDDING_MODE == "Ollama":
                base_url = settings.OLLAMA_BASE_URL.rstrip("/").removesuffix("/v1")
                self.wait_for_service("Ollama", f"{base_url}/api/tags", options["wait_timeout"])
                self.ensure_model(base_url, options["pull_timeout"])
            self.ensure_collection(options["collection"])
            call_command("migrate", interactive=False, stdout=self.stdout)
        except (URLError, OSError, ValueError) as exc:
            raise CommandError(f"Не удалось подготовить приложение: {exc}") from exc
        self.stdout.write(self.style.SUCCESS("Приложение подготовлено к запуску."))
