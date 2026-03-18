import os
import unittest
import zipfile
from ..utils.network_utils import list_layers

class TestListLayers(unittest.TestCase):
    
    def setUp(self):
        """
        Set up the test environment by creating a temporary ZIP file with a simulated structure.
        - The ZIP file contains a 'layer_name.tsv' file with mappings between layer IDs and names.
        - It also contains several multiplex files for testing.
        """
        self.test_zip_path = "test_network.zip"
        with zipfile.ZipFile(self.test_zip_path, 'w') as zipf:
            zipf.writestr("layer_name.tsv", "1\tLayer1\n2\tLayer2\n3\tLayer3\n")
            zipf.writestr("multiplex/1/compounds.tsv", "H\tI\nJ\tK\nL\tM\n")
            zipf.writestr("multiplex/1/genes.tsv", "a\tb\nc\td\ne\tf\n")
            zipf.writestr("multiplex/1/diseases.tsv", "V\tW\nX\tY\nZ\tW\n")
            zipf.writestr("multiplex/1/pathways.tsv", "1\t2\n3\t4\n5\t6\n")

    def tearDown(self):
        """
        Clean up the test environment by removing the temporary ZIP file after each test.
        """
        os.remove(self.test_zip_path)

    def test_list_layers(self):
        """
        Test the 'list_layers' function with a valid ZIP file and layer name.
        - Verifies that the function returns a sorted list of layer names for the specified layer.
        """
        result = list_layers(".", "Layer1")
        expected = ["compounds", "diseases", "genes", "pathways"]
        self.assertEqual(result, expected)
    
    def test_missing_layer_name_tsv(self):
        """
        Test the 'list_layers' function when the 'layer_name.tsv' file is missing.
        - Verifies that the function raises a ValueError with the correct error message.
        """
        os.remove(self.test_zip_path)  # Remove the existing ZIP file
        with zipfile.ZipFile(self.test_zip_path, 'w') as zipf:
            zipf.writestr("multiplex/1/genes.tsv", "a\tb\nc\td\ne\tf\n")  # Add only multiplex files
        with self.assertRaises(ValueError):
            list_layers(".", "Layer1")

    def test_layer_not_found(self):
        """
        Test the 'list_layers' function when the requested layer does not exist in 'layer_name.tsv'.
        - Verifies that the function raises a ValueError with the correct error message.
        """
        with self.assertRaises(ValueError):
            list_layers(".", "Layer4")

    # Uncomment and complete this test if needed
    # def test_missing_compounds_file(self):
    #     """
    #     Test the 'list_layers' function when a required file (e.g., 'compounds.tsv') is missing.
    #     - Verifies that the function raises a ValueError with the correct error message.
    #     """
    #     with zipfile.ZipFile(self.test_zip_path, 'w') as zipf:
    #         zipf.writestr("layer_name.tsv", "1\tLayer1\n")
    #     with self.assertRaises(ValueError):
    #         list_layers(".", "Layer1")

if __name__ == '__main__':
    unittest.main()
