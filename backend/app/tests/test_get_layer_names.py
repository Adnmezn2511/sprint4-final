import os
import unittest
from ..utils.multixrank_config import get_layer_names

class TestGetLayerNames(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a test directory and a mock 'layer_name.tsv' file.
        - The file contains mappings between layer IDs and layer names.
        - This setup ensures a controlled environment for testing.
        """
        self.test_dir = "test_layer_names"
        os.makedirs(self.test_dir, exist_ok=True)
        self.layer_file_path = os.path.join(self.test_dir, "layer_name.tsv")
        self.layer_content = "1\tCompounds\n2\tDiseases\n3\tGenes\n4\tPathways\n"
        with open(self.layer_file_path, "w", encoding="utf-8") as f:
            f.write(self.layer_content)
    
    def tearDown(self):
        """
        Clean up the test environment by removing the test directory and its contents.
        - Deletes the 'layer_name.tsv' file and the test directory after each test.
        """
        if os.path.exists(self.layer_file_path):
            os.remove(self.layer_file_path)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_get_layer_names(self):
        """
        Test the 'get_layer_names' function with a valid 'layer_name.tsv' file.
        - Verifies that the function correctly parses the file and returns the expected dictionary.
        """
        expected_output = {
            "1": "Compounds",
            "2": "Diseases",
            "3": "Genes",
            "4": "Pathways"
        }
        result = get_layer_names(self.test_dir)
        self.assertEqual(result, expected_output)
    
    def test_get_layer_names_file_missing(self):
        """
        Test the 'get_layer_names' function when the 'layer_name.tsv' file is missing.
        - Verifies that the function raises a FileNotFoundError.
        """
        os.remove(self.layer_file_path)  # Remove the file to simulate a missing file
        with self.assertRaises(FileNotFoundError):
            get_layer_names(self.test_dir)
    
    def test_get_layer_names_malformed_file(self):
        """
        Test the 'get_layer_names' function with a malformed 'layer_name.tsv' file.
        - Verifies that the function ignores malformed lines and processes valid lines correctly.
        """
        with open(self.layer_file_path, "w", encoding="utf-8") as f:
            f.write("1\tCompounds\n2\tDiseases\n3\n4\tPathways\n")  # Malformed line (missing tab)
        result = get_layer_names(self.test_dir)
        self.assertNotIn("3", result)  # The malformed line should not be included
        self.assertIn("1", result)
        self.assertIn("2", result)
        self.assertIn("4", result)  # Valid lines should still be processed correctly

    def test_empty_file(self):
        """
        Test the 'get_layer_names' function with an empty 'layer_name.tsv' file.
        - Verifies that the function returns an empty dictionary when the file is empty.
        """
        with open(self.layer_file_path, "w", encoding="utf-8") as f:
            f.write("")  # Write an empty file
        result = get_layer_names(self.test_dir)
        self.assertEqual(result, {})  # The result should be an empty dictionary
        
if __name__ == "__main__":
    unittest.main()
