import os
import unittest
import tempfile
from ..itRWR.file_utils import write_config_file

class TestWriteConfigFile(unittest.TestCase):
    
    def setUp(self):
        """
        Set up the test environment by creating a temporary directory.
        - Creates a temporary directory to simulate the configuration file and output folder.
        - Initializes paths for the configuration file and output folder.
        """
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.test_dir.name, "config.txt")
        self.out_folder = os.path.join(self.test_dir.name, "output")
        os.mkdir(self.out_folder)
    
    def tearDown(self):
        """
        Clean up the test environment by removing the temporary directory.
        - Ensures that all temporary files and directories are deleted after each test.
        """
        self.test_dir.cleanup()
    
    # def test_valid_config_file(self):
    #     """
    #     Test the 'write_config_file' function with a valid configuration file.
    #     - Verifies that the function correctly updates the seed file path in the output configuration file.
    #     - Ensures that other lines in the configuration file remain unchanged.
    #     """
    #     # Create a valid configuration file
    #     with open(self.config_file, "w") as f:
    #         f.write("seed: /old/path/seeds_1.txt\nother_config: value\n")
        
    #     # Call the function to write the updated configuration file
    #     write_config_file(self.config_file, self.out_folder, 42)
        
    #     # Verify the contents of the output configuration file
    #     config_out = os.path.join(self.out_folder, "config.txt")
    #     with open(config_out, "r") as f:
    #         lines = f.readlines()
        
    #     # Assert that the first line is updated with the new seed file path
    #     expected_first_line = f"seed: {os.path.join(self.out_folder, 'seeds_42.txt')}\n"
    #     self.assertEqual(lines[0], expected_first_line)
        
    #     # Assert that other lines remain unchanged
    #     self.assertEqual(lines[1], "other_config: value\n")
    
    def test_non_existent_config_file(self):
        """
        Test the 'write_config_file' function with a non-existent configuration file.
        - Verifies that the function raises a FileNotFoundError when the configuration file does not exist.
        """
        with self.assertRaises(FileNotFoundError):
            write_config_file("/invalid/path/config.txt", self.out_folder)
    
    def test_non_existent_output_folder(self):
        """
        Test the 'write_config_file' function with a non-existent output folder.
        - Verifies that the function raises a FileNotFoundError when the output folder does not exist.
        """
        invalid_out_folder = os.path.join(self.test_dir.name, "non_existent")
        with self.assertRaises(FileNotFoundError):
            write_config_file(self.config_file, invalid_out_folder)

if __name__ == '__main__':
    unittest.main()
