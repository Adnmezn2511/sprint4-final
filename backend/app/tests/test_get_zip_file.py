import os
import unittest
import tempfile
from ..utils.network_utils import _get_zip_file

class TestGetZipFile(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a temporary directory.
        - This directory will be used to simulate different scenarios for ZIP file detection.
        """
        self.test_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """
        Clean up the test environment by deleting the temporary directory.
        - Ensures no leftover files or directories remain after each test.
        """
        self.test_dir.cleanup()
    
    def test_no_zip_file(self):
        """
        Test the '_get_zip_file' function when no ZIP file is present in the directory.
        - Verifies that the function raises a ValueError with the correct error message.
        """
        with self.assertRaises(ValueError) as context:
            _get_zip_file(self.test_dir.name)
        self.assertEqual(str(context.exception), "Aucun fichier zip trouvé dans le dossier.")
    
    def test_single_zip_file(self):
        """
        Test the '_get_zip_file' function when a single ZIP file is present in the directory.
        - Verifies that the function correctly identifies and returns the path to the ZIP file.
        """
        zip_path = os.path.join(self.test_dir.name, "test.zip")
        with open(zip_path, "w"):  # Create an empty ZIP file
            pass
        
        result = _get_zip_file(self.test_dir.name)
        self.assertEqual(result, zip_path)
    
    def test_multiple_zip_files(self):
        """
        Test the '_get_zip_file' function when multiple ZIP files are present in the directory.
        - Verifies that the function raises a ValueError with the correct error message.
        """
        # Create multiple ZIP files in the directory
        open(os.path.join(self.test_dir.name, "test1.zip"), "w").close()
        open(os.path.join(self.test_dir.name, "test2.zip"), "w").close()
        
        with self.assertRaises(ValueError) as context:
            _get_zip_file(self.test_dir.name)
        self.assertEqual(str(context.exception), "Plusieurs fichiers zip trouvés dans le dossier. Veuillez n'en fournir qu'un seul.")

if __name__ == "__main__":
    unittest.main()
