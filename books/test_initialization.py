import json
from io import BytesIO, StringIO
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.core.management import call_command, CommandError
from django.test import SimpleTestCase, override_settings
from qdrant_client.models import Distance


def response(data):
    return BytesIO(json.dumps(data).encode())


@override_settings(
    EMBEDDING_MODE="Ollama",
    OLLAMA_BASE_URL="http://ollama:11434/v1/",
    OLLAMA_EMBEDDING_MODEL="embeddinggemma",
    QDRANT_URL="http://qdrant:6333",
)
class InitializationTests(SimpleTestCase):
    @patch("books.management.commands.initialize_services.call_command")
    @patch("books.management.commands.initialize_services.get_dimension", return_value=768)
    @patch("books.management.commands.initialize_services.QdrantManager")
    @patch("books.management.commands.initialize_services.urlopen")
    def test_cached_model_and_new_collection(self, request, manager, dimension, migrate):
        request.side_effect = [response({}), response({}), response({"details": {}})]
        manager.return_value.client.collection_exists.return_value = False
        call_command("initialize_services", stdout=StringIO())
        manager.return_value.create_collection.assert_called_once_with(
            collection_name="sample_collection", size=768
        )
        self.assertFalse(
            any("/api/pull" in call.args[0].full_url for call in request.call_args_list)
        )
        migrate.assert_called_once()
        self.assertEqual(migrate.call_args.args[0], "migrate")

    @patch("books.management.commands.initialize_services.call_command")
    @patch("books.management.commands.initialize_services.get_dimension", return_value=768)
    @patch("books.management.commands.initialize_services.QdrantManager")
    @patch("books.management.commands.initialize_services.urlopen")
    def test_missing_model_is_downloaded(self, request, manager, dimension, migrate):
        request.side_effect = [
            response({}),
            response({}),
            HTTPError("http://ollama/api/show", 404, "Not found", {}, None),
            response({"status": "success"}),
        ]
        manager.return_value.client.collection_exists.return_value = False
        call_command("initialize_services", stdout=StringIO())
        pull = request.call_args_list[-1].args[0]
        self.assertEqual(pull.full_url, "http://ollama:11434/api/pull")
        self.assertEqual(json.loads(pull.data), {"model": "embeddinggemma", "stream": False})

    @patch("books.management.commands.initialize_services.call_command")
    @patch("books.management.commands.initialize_services.get_dimension", return_value=768)
    @patch("books.management.commands.initialize_services.QdrantManager")
    @patch("books.management.commands.initialize_services.urlopen")
    def test_existing_collection_is_preserved(self, request, manager, dimension, migrate):
        request.side_effect = [response({}), response({}), response({})]
        manager.return_value.client.collection_exists.return_value = True
        manager.return_value.client.get_collection.return_value = SimpleNamespace(
            config=SimpleNamespace(
                params=SimpleNamespace(vectors=SimpleNamespace(size=768, distance=Distance.COSINE))
            )
        )
        call_command("initialize_services", stdout=StringIO())
        manager.return_value.create_collection.assert_not_called()
        manager.return_value.client.delete_collection.assert_not_called()

    @patch("books.management.commands.initialize_services.call_command")
    @patch("books.management.commands.initialize_services.get_dimension", return_value=768)
    @patch("books.management.commands.initialize_services.QdrantManager")
    @patch("books.management.commands.initialize_services.urlopen")
    def test_incompatible_collection_stops_initialization_without_deleting_data(
        self, request, manager, dimension, migrate
    ):
        request.side_effect = [response({}), response({}), response({})]
        manager.return_value.client.collection_exists.return_value = True
        manager.return_value.client.get_collection.return_value = SimpleNamespace(
            config=SimpleNamespace(
                params=SimpleNamespace(vectors=SimpleNamespace(size=384, distance=Distance.COSINE))
            )
        )
        with self.assertRaises(CommandError):
            call_command("initialize_services", stdout=StringIO())
        manager.return_value.create_collection.assert_not_called()
        manager.return_value.client.delete_collection.assert_not_called()
        migrate.assert_not_called()

    @patch("books.management.commands.initialize_services.sleep")
    @patch("books.management.commands.initialize_services.monotonic", side_effect=[0, 0, 2])
    @patch("books.management.commands.initialize_services.urlopen", side_effect=URLError("offline"))
    def test_unavailable_service_has_a_bounded_wait(self, request, clock, sleep):
        with self.assertRaises(CommandError):
            call_command("initialize_services", wait_timeout=1, stdout=StringIO())
