import unittest
from unittest.mock import Mock, patch
import json
from rest_framework.test import APIRequestFactory
from app.views import (
    getMultipatientGraph,
    getGraph,
    input_zip_path,
    layers_list,
    log_zip_dir,
    multiplex_list,
    result_dir,
    unique_nodes,
    upload_zip,
    upload_seed,
)
from app.views import (
    getMultipatientGraph,
    getGraph,
    input_zip_path,
    layers_list,
    log_zip_dir,
    multiplex_list,
    result_dir,
    unique_nodes,
    upload_zip,
    upload_seed,
)

# Create a factory for generating mock API requests
factory = APIRequestFactory()

class TestViews(unittest.TestCase):

    @patch('app.views.list_multiplex_networks')
    def test_multiplex_list(self, mock_list):
        """
        Test the 'multiplex_list' view.
        - Mocks the 'list_multiplex_networks' function to simulate the response.
        - Verifies that the view returns a 200 status code.
        - Verifies that the response contains the expected list of multiplex networks.
        """
        mock_list.return_value = ['multiplex1', 'multiplex2']
        request = factory.get('/fake-url/')
        response = multiplex_list(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'multiplexes': ['multiplex1', 'multiplex2']})

    @patch('app.views.list_layers')
    def test_layers_list(self, mock_list):
        """
        Test the 'layers_list' view.
        - Mocks the 'list_layers' function to simulate the response.
        - Verifies that the view returns a 200 status code.
        - Verifies that the response contains the expected list of layers for a given multiplex.
        """
        mock_list.return_value = ['layer1', 'layer2']
        request = factory.get('/fake-url/')
        response = layers_list(request, 'test_multiplex')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'layers': ['layer1', 'layer2']})

    @patch('app.views.list_unique_nodes')
    def test_unique_nodes(self, mock_list):
        """
        Test the 'unique_nodes' view.
        - Mocks the 'list_unique_nodes' function to simulate the response.
        - Verifies that the view returns a 200 status code.
        - Verifies that the response contains the expected list of unique nodes for a given multiplex and layer.
        """
        mock_list.return_value = ['node1', 'node2']
        request = factory.get('/fake-url/')
        response = unique_nodes(request, 'multiplex1', 'layer1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'nodes': ['node1', 'node2']})

    def test_upload_zip_without_file(self):
        """
        Test the 'upload_zip' view when no file is provided in the request.
        - Simulates a POST request without a file.
        - Verifies that the view returns a 400 status code.
        - Verifies that the response contains the expected error message.
        """
        request = factory.post('/fake-url/', {}, format='multipart')
        request.FILES.clear()
        response = upload_zip(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {"error": "A file is required"})

    @patch("app.views.run_itRWR_multipatient")
    def test_get_multipatient_graph_success(self, mock_run_itRWR_multipatient):
        """
        Test the 'getMultipatientGraph' API view.
        - Mocks the multipatient controller execution.
        - Verifies that the API returns serialized figures with status 200.
        - Verifies that controller is called with expected converted parameters.
        """
        fig_1 = Mock()
        fig_1.to_dict.return_value = {"figure": "patient_1"}
        fig_2 = Mock()
        fig_2.to_dict.return_value = {"figure": "patient_2"}
        merged_fig = Mock()
        merged_fig.to_dict.return_value = {"figure": "merged"}
        merged_modules_fig = Mock()
        merged_modules_fig.to_dict.return_value = {"figure": "merged_modules"}
        mock_run_itRWR_multipatient.return_value = (
            {
                "BR664F": {"figure": fig_1, "modules": []},
                "BR101A": {"figure": fig_2, "modules": []},
            },
            merged_fig,
            merged_modules_fig,
        )

        payload = {
            "dico_patient_seeds": {
                "BR664F": ["GENE1", "GENE2"],
                "BR101A": ["GENE3"],
            },
            "steps": "5",
            "top": "10",
            "restart": "0.7",
            "user": "test_user",
        }

        request = factory.post("/api/graph/multipatient/", payload, format="json")
        response = getMultipatientGraph(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"figure": "patient_1", "_modules": []},
                {"figure": "patient_2", "_modules": []},
                {"figure": "merged"},
                {"figure": "merged_modules"},
            ],
        )

        mock_run_itRWR_multipatient.assert_called_once_with(
            log_zip_dir,
            input_zip_path,
            result_dir,
            payload["dico_patient_seeds"],
            5,
            10,
            0.7,
            "test_user",
        )

    @patch("app.views.run_itRWR_multipatient")
    def test_get_multipatient_graph_empty_seeds_returns_400(self, mock_run_itRWR_multipatient):
        """
        Negative test for 'getMultipatientGraph' when a patient has an empty seed list.
        - Mocks controller validation error.
        - Verifies the API returns HTTP 400 with the error payload.
        """
        payload = {
            "dico_patient_seeds": {
                "BR664F": [],
            },
            "steps": "5",
            "top": "10",
            "restart": "0.7",
            "user": "test_user",
        }

        request = factory.post("/api/graph/multipatient/", payload, format="json")
        response = getMultipatientGraph(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Patient 'BR664F' must have a non-empty seed list"})
        mock_run_itRWR_multipatient.assert_not_called()

    @patch("app.views.run_itRWR_multipatient")
    def test_get_multipatient_graph_restart_out_of_range_returns_400(self, mock_run_itRWR_multipatient):
        payload = {
            "dico_patient_seeds": {
                "BR664F": ["GENE1"],
            },
            "steps": "5",
            "top": "10",
            "restart": "1.2",
            "user": "test_user",
        }

        request = factory.post("/api/graph/multipatient/", payload, format="json")
        response = getMultipatientGraph(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "restart must be between 0 and 1 (exclusive)"})
        mock_run_itRWR_multipatient.assert_not_called()

    def test_upload_seed_file_without_file(self):
        """
        Test the 'upload-seed' view when no file is provided in the request.
        - Simulates a POST request without a file.
        - Verifies that the view returns a 400 status code.
        - Verifies that the response contains the expected error message.
        """
        request = factory.post('/fake-url/', {}, format='multipart')
        request.FILES.clear()
        response = upload_seed(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {"error": "A file is required"})

if __name__ == '__main__':
    unittest.main()
