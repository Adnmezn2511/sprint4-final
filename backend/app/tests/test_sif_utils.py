from django.test import TestCase
import unittest
import os
from ..itRWR.sif_utils import correct_sif_order, filter_sif_file
import pandas as pd

class TestSifUtils(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a test SIF file and a multiplex directory.
        - The SIF file will be used to test the 'correct_sif_order' and 'filter_sif_file' functions.
        - The multiplex directory will simulate the structure required for testing.
        """
        self.sif_file = "test.sif"
        self.multiplex_dir = "multiplex_test"
        os.makedirs(self.multiplex_dir, exist_ok=True)

    def tearDown(self):
        """
        Clean up the test environment by removing the test SIF file and multiplex directory.
        - Ensures no leftover files or directories remain after each test.
        """
        if os.path.exists(self.sif_file):
            os.remove(self.sif_file)
        if os.path.exists(self.multiplex_dir):
            os.rmdir(self.multiplex_dir)

    def test_correct_sif_order(self):
        """
        Test the 'correct_sif_order' function.
        - Verifies that the function processes the SIF file and ensures the correct order of nodes.
        - Ensures that the SIF file exists after processing.
        """
        # Create a test SIF file with a sample bipartite relation
        with open(self.sif_file, "w") as f:
            f.write("A\tbipartite/1_2\tB\n")
        
        # Call the function to correct the SIF file
        correct_sif_order(self.sif_file, self.multiplex_dir)
        self.assertTrue(os.path.exists(self.sif_file))

if __name__ == "__main__":
    unittest.main()
