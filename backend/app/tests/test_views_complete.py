import unittest
import json
import io
import zipfile
import os
import tempfile
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

factory = APIRequestFactory()


class TestGetGraph(unittest.TestCase):

    @patch("app.views.run_itRWR")
    def test_getgraph_valid(self, mock_run):
        from app.views import getGraph
        mock_fig = MagicMock()
        mock_fig.to_dict.return_value = {"data": [], "layout": {}}
        mock_run.return_value = mock_fig
        payload = {"seeds": ["GeneA"], "steps": 1, "top": 5, "restart": 0.7, "user": "u", "title": "t"}
        request = factory.post("/graph/", json.dumps(payload), content_type="application/json")
        response = getGraph(request)
        self.assertEqual(response.status_code, 200)

    @patch("app.views.run_itRWR")
    def test_getgraph_default_params(self, mock_run):
        from app.views import getGraph
        mock_fig = MagicMock()
        mock_fig.to_dict.return_value = {"data": []}
        mock_run.return_value = mock_fig
        payload = {}
        request = factory.post("/graph/", json.dumps(payload), content_type="application/json")
        response = getGraph(request)
        self.assertEqual(response.status_code, 200)

    @patch("app.views.run_itRWR")
    def test_getgraph_invalid_steps(self, mock_run):
        from app.views import getGraph
        payload = {"seeds": ["G"], "steps": "not_int", "top": 5, "restart": 0.7}
        request = factory.post("/graph/", json.dumps(payload), content_type="application/json")
        response = getGraph(request)
        self.assertEqual(response.status_code, 400)

    @patch("app.views.run_itRWR")
    def test_getgraph_invalid_restart(self, mock_run):
        from app.views import getGraph
        payload = {"seeds": ["G"], "steps": 1, "top": 5, "restart": "bad"}
        request = factory.post("/graph/", json.dumps(payload), content_type="application/json")
        response = getGraph(request)
        self.assertEqual(response.status_code, 400)

    @patch("app.views.run_itRWR", side_effect=Exception("Algo failed"))
    def test_getgraph_exception_propagates(self, mock_run):
        from app.views import getGraph
        payload = {"seeds": ["G"], "steps": 1, "top": 5, "restart": 0.3, "user": "u", "title": "t"}
        request = factory.post("/graph/", json.dumps(payload), content_type="application/json")
        with self.assertRaises(Exception):
            getGraph(request)


class TestUploadZip(unittest.TestCase):

    def test_upload_valid_zip(self):
        from app.views import upload_zip
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr("test.txt", "hello")
        buf.seek(0)
        buf.name = "input.zip"
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.views.current_zip_dir", tmpdir):
                request = factory.post("/upload-zip", {"file": buf}, format="multipart")
                response = upload_zip(request)
        self.assertEqual(response.status_code, 200)

    def test_upload_non_zip_file(self):
        from app.views import upload_zip
        buf = io.BytesIO(b"not a zip")
        buf.name = "file.txt"
        request = factory.post("/upload-zip", {"file": buf}, format="multipart")
        response = upload_zip(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("ZIP", json.loads(response.content)["error"])

    def test_upload_no_file(self):
        from app.views import upload_zip
        request = factory.post("/upload-zip", {}, format="multipart")
        response = upload_zip(request)
        self.assertEqual(response.status_code, 400)


class TestTestApi(unittest.TestCase):

    def test_test_api_returns_200(self):
        from app.views import test_api
        request = factory.get("/test/")
        response = test_api(request)
        self.assertEqual(response.status_code, 200)

    def test_test_api_content(self):
        from app.views import test_api
        request = factory.get("/test/")
        response = test_api(request)
        self.assertIn("test", response.data)


class TestDownloadZip(unittest.TestCase):

    def test_download_zip_no_dir(self):
        from app.views import download_zip
        from django.http import Http404
        request = factory.get("/download-zip/1/")
        with patch("app.views.log_zip_dir", "/nonexistent/path"):
            with self.assertRaises(Http404):
                download_zip(request, 1)

    def test_download_zip_no_matching_file(self):
        from app.views import download_zip
        from django.http import Http404
        request = factory.get("/download-zip/999/")
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.views.log_zip_dir", tmpdir):
                with self.assertRaises(Http404):
                    download_zip(request, 999)

    def test_download_zip_success(self):
        from app.views import download_zip
        import gc
        request = factory.get("/download-zip/1/")
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "sample#1.zip")
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("file.txt", "content")
            with patch("app.views.log_zip_dir", tmpdir):
                response = download_zip(request, 1)
                self.assertEqual(response.status_code, 200)
                # Ferme le FileResponse avant que TemporaryDirectory tente de supprimer
                if hasattr(response, 'file_to_stream') and response.file_to_stream:
                    response.file_to_stream.close()
                elif hasattr(response, 'streaming_content'):
                    # Force close en consommant le stream
                    try:
                        list(response.streaming_content)
                    except Exception:
                        pass
                gc.collect()


class TestMultiplexListView(unittest.TestCase):

    @patch("app.views.list_multiplex_networks")
    def test_multiplex_list_ok(self, mock_list):
        from app.views import multiplex_list
        mock_list.return_value = ["A", "B"]
        request = factory.get("/api/multiplexes/")
        response = multiplex_list(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"multiplexes": ["A", "B"]})

    @patch("app.views.list_multiplex_networks")
    def test_multiplex_list_empty(self, mock_list):
        from app.views import multiplex_list
        mock_list.return_value = []
        request = factory.get("/api/multiplexes/")
        response = multiplex_list(request)
        self.assertEqual(json.loads(response.content), {"multiplexes": []})


class TestLayersListView(unittest.TestCase):

    @patch("app.views.list_layers")
    def test_layers_list_ok(self, mock_list):
        from app.views import layers_list
        mock_list.return_value = ["layer1", "layer2"]
        request = factory.get("/api/multiplexes/mp1/layers/")
        response = layers_list(request, "mp1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"layers": ["layer1", "layer2"]})


class TestUniqueNodesView(unittest.TestCase):

    @patch("app.views.list_unique_nodes")
    def test_unique_nodes_ok(self, mock_list):
        from app.views import unique_nodes
        mock_list.return_value = ["node1", "node2"]
        request = factory.get("/api/multiplexes/mp1/layers/l1/nodes/")
        response = unique_nodes(request, "mp1", "l1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"nodes": ["node1", "node2"]})


if __name__ == "__main__":
    unittest.main()