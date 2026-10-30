from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase


class DeploymentCommandTests(SimpleTestCase):
    @patch("books.management.commands.make_qdrant_collection.get_dimension", return_value=768)
    @patch("books.management.commands.make_qdrant_collection.QdrantManager")
    def test_collection_command_is_noninteractive(self, manager, dimension):
        manager.return_value.client.collection_exists.return_value = False
        call_command("make_qdrant_collection", stdout=StringIO())
        manager.return_value.create_collection.assert_called_once_with(
            collection_name="sample_collection", size=768
        )

    @patch("books.management.commands.make_qdrant_collection.get_dimension")
    @patch("books.management.commands.make_qdrant_collection.QdrantManager")
    def test_existing_collection_is_preserved(self, manager, dimension):
        manager.return_value.client.collection_exists.return_value = True
        call_command("make_qdrant_collection", stdout=StringIO())
        manager.return_value.create_collection.assert_not_called()
        dimension.assert_not_called()

    @patch("books.management.commands.enrich_book_collection.enrich_book_collection", return_value=47)
    def test_import_defaults_to_catalog_in_project(self, importer):
        call_command("enrich_book_collection", stdout=StringIO())
        importer.assert_called_once_with(
            collection_name="sample_collection", json_file=settings.BASE_DIR / "task/books.json"
        )
