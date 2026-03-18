import unittest
import zipfile
import tempfile
from ..utils.network_utils import _get_layer_mapping

class TestGetLayerMapping(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a temporary ZIP file.
        - Adds a valid 'layer_name.tsv' file to the ZIP with predefined content.
        - The file contains mappings between layer IDs and layer names.
        """
        self.temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        with zipfile.ZipFile(self.temp_zip.name, 'w') as zipf:
            zipf.writestr("layer_name.tsv", "1\tlayer1\n2\tlayer2\n3\tlayer3\n")
    
    def tearDown(self):
        """
        Clean up the test environment by closing and deleting the temporary ZIP file.
        """
        self.temp_zip.close()

    def test_valid_layer_mapping(self):
        """
        Test the '_get_layer_mapping' function with a valid 'layer_name.tsv' file.
        - Verifies that the function correctly extracts the layers and their mappings.
        - Asserts that the returned layers list matches the expected order.
        - Asserts that the returned mapping dictionary matches the expected key-value pairs.
        """
        with zipfile.ZipFile(self.temp_zip.name, 'r') as zipf:
            layers, mapping = _get_layer_mapping(zipf)
        
        # Assert that the layers are correctly extracted
        self.assertEqual(layers, ["layer1", "layer2", "layer3"])
        
        # Assert that the mapping is correctly extracted
        self.assertEqual(mapping, {"layer1": "1", "layer2": "2", "layer3": "3"})
    
    def test_missing_layer_name_tsv(self):
        """
        Test the '_get_layer_mapping' function when 'layer_name.tsv' is missing.
        - Creates a ZIP file without the required 'layer_name.tsv' file.
        - Verifies that the function raises a ValueError with the correct error message.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as empty_zip:
            with zipfile.ZipFile(empty_zip.name, 'w') as zipf:
                zipf.writestr("other_file.txt", "some content")  # Add a different file
            
            with zipfile.ZipFile(empty_zip.name, 'r') as zipf:
                # Assert that a ValueError is raised when 'layer_name.tsv' is missing
                with self.assertRaises(ValueError) as context:
                    _get_layer_mapping(zipf)
                
                # Assert that the error message matches the expected message
                self.assertEqual(str(context.exception), "Le fichier 'layer_name.tsv' n'a pas été trouvé dans le zip.")

if __name__ == "__main__":
    unittest.main()
