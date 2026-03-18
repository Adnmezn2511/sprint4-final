import os
import zipfile
import unittest
from ..utils.multixrank_config import create_arborescence_from_zip

class TestCreateArborescenceFromZip(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a mock ZIP file with a predefined folder and file structure.
        - Creates a ZIP file named 'test_arborescence.zip'.
        - Defines the destination directory where the ZIP contents will be extracted.
        - Adds files with content to the ZIP file to simulate a real-world scenario.
        """
        self.zip_path = "test_arborescence.zip"
        self.destination_path = "output_arborescence"
        
        # Define the mock ZIP file content
        self.zip_content = {
            "folder1/file1.txt": b"Hello, World!",
            "folder1/file2.txt": b"Python Unittest",
            "folder2/file3.txt": b"Test File",
        }
        
        # Create the ZIP file with the specified content
        with zipfile.ZipFile(self.zip_path, 'w') as zipf:
            for file_name, content in self.zip_content.items():
                zipf.writestr(file_name, content)
    
    def tearDown(self):
        """
        Clean up the test environment by removing the created ZIP file and the extracted directory.
        - Deletes the ZIP file created during the setup.
        - Recursively deletes the destination directory and its contents.
        """
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        if os.path.exists(self.destination_path):
            for root, dirs, files in os.walk(self.destination_path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(self.destination_path)
    
    def test_create_arborescence_from_zip(self):
        """
        Test the 'create_arborescence_from_zip' function to ensure it correctly extracts the ZIP file contents.
        - Verifies that the folders ('folder1', 'folder2') are created in the destination directory.
        - Verifies that all files in the ZIP file are extracted to their respective locations.
        """
        # Call the function to extract the ZIP file
        create_arborescence_from_zip(self.zip_path, self.destination_path)
        
        # Check that the folders have been extracted
        self.assertTrue(os.path.exists(os.path.join(self.destination_path, "folder1")))
        self.assertTrue(os.path.exists(os.path.join(self.destination_path, "folder2")))
        
        # Check that the files have been extracted
        for file_name in self.zip_content.keys():
            extracted_file = os.path.join(self.destination_path, file_name)
            self.assertTrue(os.path.exists(extracted_file))

if __name__ == "__main__":
    unittest.main()
