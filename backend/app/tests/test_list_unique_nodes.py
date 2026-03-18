import unittest
import zipfile
import os
from ..utils.network_utils import list_unique_nodes

class TestListUniqueNodes(unittest.TestCase):
    
    def setUp(self):
        """
        Set up the test environment by creating a temporary ZIP file with a simulated structure.
        - The ZIP file contains a 'layer_name.tsv' file with mappings between layer IDs and names.
        - It also contains a multiplex file for testing unique node extraction.
        """
        self.test_zip_path = "test_network.zip"
        with zipfile.ZipFile(self.test_zip_path, 'w') as zipf:
            zipf.writestr("layer_name.tsv", "1\tLayer1\n2\tLayer2\n")
            zipf.writestr("multiplex/1/compounds.tsv", "A\tB\nB\tC\nB\tD\n")

    def tearDown(self):
        """
        Clean up the test environment by removing the temporary ZIP file after each test.
        """
        os.remove(self.test_zip_path)
    
    def test_list_unique_nodes(self):
        """
        Test the 'list_unique_nodes' function with a valid ZIP file and layer name.
        - Verifies that the function correctly extracts and returns a sorted list of unique nodes.
        """
        result = list_unique_nodes(".", "Layer1", "compounds")
        expected = ["A", "B", "C", "D"]
        self.assertEqual(result, expected)

    def test_missing_layer_name_tsv(self):
        """
        Test the 'list_unique_nodes' function when the 'layer_name.tsv' file is missing.
        - Verifies that the function raises a ValueError with the correct error message.
        """
        os.remove(self.test_zip_path)
        with zipfile.ZipFile(self.test_zip_path, 'w') as zipf:
            zipf.writestr("multiplex/1/compounds.tsv", "A\tB\nB\tC\nB\tD\n")
        with self.assertRaises(ValueError):
            list_unique_nodes(".", "Layer1", "compounds")
    
    def test_layer_not_found(self):
        """
        Test the 'list_unique_nodes' function when the requested layer does not exist in 'layer_name.tsv'.
        - Verifies that the function raises a ValueError with the correct error message.
        """
        with self.assertRaises(ValueError):
            list_unique_nodes(".", "Layer3", "compounds")
    
    def test_missing_compounds_file(self):
        """
        Test the 'list_unique_nodes' function when the specified file (e.g., 'compounds.tsv') is missing.
        - Verifies that the function raises a ValueError with the correct error message.
        """
        with zipfile.ZipFile(self.test_zip_path, 'w') as zipf:
            zipf.writestr("layer_name.tsv", "1\tLayer1\n")
        with self.assertRaises(ValueError):
            list_unique_nodes(".", "Layer2", "compounds")
    
    def test_empty_compounds_file(self):
        """
        Test the 'list_unique_nodes' function when the specified file (e.g., 'compounds.tsv') is empty.
        - Verifies that the function returns an empty list.
        """
        os.remove(self.test_zip_path)
        with zipfile.ZipFile(self.test_zip_path, 'w') as zipf:
            zipf.writestr("layer_name.tsv", "1\tLayer1\n")
            zipf.writestr("multiplex/1/compounds.tsv", "")
        result = list_unique_nodes(".", "Layer1", "compounds")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
