import os
import zipfile
import unittest
import yaml
from unittest.mock import patch, mock_open
from ..utils.multixrank_config import generate_config

class TestGenerateConfig(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a mock ZIP file and initializing test parameters.
        - Creates a ZIP file named 'test_data.zip' with predefined content.
        - Defines the output directory, seeds, and other parameters for the test.
        """
        self.zip_path = "test_data.zip"
        self.nbIteration = 2
        self.seeds = ["gene1", "gene2", "gene3"]
        self.path = "output_directory"
        
        # Define the mock ZIP file content
        self.zip_content = {
            "multiplex/1/layer1.tsv": b"content1",
            "multiplex/2/layer2.tsv": b"content2",
            "bipartite/1_2.tsv": b"geneA\tgeneB\n",
        }
        
        # Create the ZIP file with the specified content
        with zipfile.ZipFile(self.zip_path, 'w') as zipf:
            for file_name, content in self.zip_content.items():
                zipf.writestr(file_name, content)
    
    def tearDown(self):
        """
        Clean up the test environment by removing the created ZIP file and output directory.
        - Deletes the ZIP file created during the setup.
        - Recursively deletes the output directory and its contents.
        """
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        if os.path.exists(self.path):
            for root, dirs, files in os.walk(self.path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(self.path)
    
    def test_generate_config(self):
        """
        Test the 'generate_config' function to ensure it correctly processes the ZIP file and generates the required output.
        - Verifies that the output directory is created.
        - Verifies that the YAML configuration file is created and contains the expected keys.
        - Verifies that the seeds file is created and contains the expected seeds.
        """
        # Call the function to generate the configuration
        generate_config(self.zip_path, self.nbIteration, self.seeds, False, self.path)
        
        # Verify that the output directory is created
        self.assertTrue(os.path.exists(self.path))
        
        # Verify that the YAML configuration file is created
        config_path = os.path.join(self.path, f"config.yml")
        self.assertTrue(os.path.exists(config_path))
        
        # Verify the content of the YAML configuration file
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        self.assertIn("multiplex", config_data)  # Check that the 'multiplex' key is present
        self.assertIn("bipartite", config_data)  # Check that the 'bipartite' key is present
        
        # Verify that the seeds file is created
        seeds_path = os.path.join(self.path, f"seeds.txt")
        self.assertTrue(os.path.exists(seeds_path))
        
        # Verify the content of the seeds file
        with open(seeds_path, "r") as f:
            seeds_content = f.read().splitlines()
        self.assertEqual(seeds_content, self.seeds)

if __name__ == "__main__":
    unittest.main()
