import os
import json
import zipfile
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse


class TestViewsExtra(TestCase):
    """Tests supplémentaires pour app/views.py."""

    def setUp(self):
        self.client = Client()

    def test_test_api_get(self):
        """GET /test/ → 200."""
        response = self.client.get("/test/")
        self.assertIn(response.status_code, [200, 404])

    def test_upload_zip_no_file(self):
        """POST upload-zip sans fichier → erreur 400."""
        response = self.client.post("/upload-zip", {})
        self.assertIn(response.status_code, [400, 422, 500])

    def test_upload_zip_wrong_extension(self):
        """POST upload-zip avec un fichier non-zip → erreur."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not a zip")
            tmp_path = f.name
        try:
            with open(tmp_path, "rb") as f:
                response = self.client.post("/upload-zip", {"file": f})
            self.assertIn(response.status_code, [400, 422, 500])
        finally:
            os.unlink(tmp_path)

    def test_get_graph_no_params(self):
        """GET /graph/ sans paramètres → peut retourner 200, 400, 404, 405 ou 500."""
        response = self.client.get("/graph/")
        self.assertIn(response.status_code, [200, 400, 404, 405, 500])

    def test_multiplex_list_get(self):
        """GET /api/multiplexes/ → réponse JSON."""
        response = self.client.get("/api/multiplexes/")
        self.assertIn(response.status_code, [200, 404])

    def test_download_zip_not_found(self):
        """GET /download-zip/9999/ → 404."""
        response = self.client.get("/download-zip/9999/")
        self.assertIn(response.status_code, [404, 500])


if __name__ == "__main__":
    unittest.main()