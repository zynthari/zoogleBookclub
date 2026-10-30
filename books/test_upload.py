from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, override_settings


@override_settings(
    CSRF_TRUSTED_ORIGINS=["http://localhost:5173"],
    MAX_FILE_SIZE=1024,
)
class LibraryUploadTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def csrf_token(self):
        response = self.client.get("/books/csrf")
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)
        return response.json()["csrfToken"]

    @patch("books.views.enrich_book_collection", return_value=2)
    def test_upload_with_csrf_and_vite_origin(self, importer):
        token = self.csrf_token()
        response = self.client.post(
            "/books/upload_library",
            {"file": SimpleUploadedFile("books.json", b'{"books": []}')},
            HTTP_X_CSRFTOKEN=token,
            HTTP_ORIGIN="http://localhost:5173",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("2", response.content.decode())
        self.assertEqual(importer.call_args.kwargs["json_file"].name, "books.json")

    @patch("books.views.enrich_book_collection")
    def test_upload_without_csrf_is_rejected(self, importer):
        response = self.client.post(
            "/books/upload_library",
            {"file": SimpleUploadedFile("books.json", b"{}")},
        )
        self.assertEqual(response.status_code, 403)
        importer.assert_not_called()

    @patch("books.views.enrich_book_collection", return_value=0)
    def test_same_origin_upload_on_custom_port(self, importer):
        token = self.csrf_token()
        response = self.client.post(
            "/books/upload_library",
            {"file": SimpleUploadedFile("books.json", b'{"books": []}')},
            HTTP_HOST="localhost:8080",
            HTTP_ORIGIN="http://localhost:8080",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        importer.assert_called_once()

    @patch("books.views.enrich_book_collection")
    def test_missing_or_invalid_file_does_not_reach_import(self, importer):
        token = self.csrf_token()
        for data in (
            {},
            {"file": SimpleUploadedFile("books.txt", b"{}")},
            {"file": SimpleUploadedFile("books.json", b"x" * 1025)},
        ):
            with self.subTest(data=data):
                response = self.client.post(
                    "/books/upload_library", data, HTTP_X_CSRFTOKEN=token
                )
                self.assertEqual(response.status_code, 400)
        importer.assert_not_called()

    def test_upload_requires_post(self):
        self.assertEqual(self.client.get("/books/upload_library").status_code, 405)
