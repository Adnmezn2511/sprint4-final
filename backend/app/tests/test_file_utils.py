import unittest
from unittest.mock import mock_open, patch
from ..itRWR.file_utils import write_config_file, read_seeds

class TestFileUtils(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="old_seed_path\nother_config\n")
    @patch("os.path.join", side_effect=lambda *args: "/".join(args)) 
    def test_write_config_file(self, mock_path_join, mock_file):
        """
        Test the 'write_config_file' function to ensure it correctly writes the updated configuration file.
        
        - Mocks the 'open' function to simulate file reading and writing.
        - Mocks 'os.path.join' to simulate path joining behavior.
        - Verifies that the first line of the output file is replaced with the new seed file path.
        - Verifies that the remaining lines of the input file are written unchanged.
        """
        # Call the function to write the configuration file
        write_config_file("config.txt", "output_folder")
        
        # Assert that the new seed file path is written as the first line
        mock_file().write.assert_any_call("seed: output_folder/seeds.txt\n")  
        
        # Assert that the other configuration lines are written unchanged
        mock_file().write.assert_any_call("other_config\n")  
    
    @patch("builtins.open", new_callable=mock_open, read_data="123\n456\n789\n")
    def test_read_seeds(self, mock_file):
        """
        Test the 'read_seeds' function to ensure it correctly reads and returns a set of seeds from a file.
        
        - Mocks the 'open' function to simulate reading a seeds file.
        - Verifies that the function returns a set containing all the seeds from the file.
        """
        # Call the function to read seeds from the mocked file
        result = read_seeds("seeds.txt")
        
        # Assert that the returned set matches the expected seeds
        self.assertEqual(result, {"123", "456", "789"}) 

if __name__ == "__main__":
    unittest.main()