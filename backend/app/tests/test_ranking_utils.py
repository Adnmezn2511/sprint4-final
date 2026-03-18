from django.test import TestCase
import unittest
from unittest import mock
import pandas as pd
from ..itRWR.ranking_utils import extract_multiplex_value, update_seeds_from_iteration, get_multiplex_rankings

class TestRankingUtils(unittest.TestCase):
    def test_extract_multiplex_value(self):
        """
        Test the 'extract_multiplex_value' function.
        - Verifies that the function correctly extracts the multiplex value from a valid string.
        - Ensures that it returns an empty string when the input format is invalid.
        """
        self.assertEqual(extract_multiplex_value("multiplex/3/genes.tsv"), "3")
        self.assertEqual(extract_multiplex_value("multiplex/2/other.tsv"), "2")
        self.assertEqual(extract_multiplex_value("error"), "")

    def test_update_seeds_from_iteration(self):
        """
        Test the 'update_seeds_from_iteration' function.
        - Verifies that the function correctly adds the first node from the ranking file to the seeds set.
        - Ensures that the added node is also included in the 'added_nodes' set.
        """
        ranking_files = [pd.DataFrame({"node": ["A", "B", "C"]})]
        seeds = {"X"}
        added_nodes = set()
        update_seeds_from_iteration(ranking_files, seeds, added_nodes)
        self.assertTrue("A" in seeds)
        self.assertTrue("A" in added_nodes)

    @mock.patch("glob.glob")
    @mock.patch("pandas.read_csv")
    def test_get_multiplex_rankings(self, mock_read_csv, mock_glob):
        """
        Test the 'get_multiplex_rankings' function.
        - Mocks the 'glob.glob' function to simulate the presence of multiple ranking files.
        - Mocks 'pandas.read_csv' to simulate reading DataFrames from the ranking files.
        - Verifies that the function correctly reads and returns a list of DataFrames for all ranking files.
        """
        # Simulating file paths returned by glob
        mock_glob.return_value = ["multiplex_1.tsv", "multiplex_2.tsv", "multiplex_3.tsv"]

        # Creating mock DataFrames for the function to return
        data_1 = pd.DataFrame({"multiplex": [1, 1, 1], "node": ["c1_A", "c1_C", "c1_B"], "score": [0.721995, 0.046153, 0.040715]})
        data_2 = pd.DataFrame({"multiplex": [2, 2, 2, 2], "node": ["c2_C", "c2_A", "c2_D", "c2_B"], "score": [0.078916, 0.014289, 0.007183, 0.006692]})
        data_3 = pd.DataFrame({"multiplex": [3, 3, 3, 3, 3], "node": ["c3_E", "c3_C", "c3_A", "c3_D", "c3_B"], "score": [0.073272, 0.002996, 0.002766, 0.002766, 0.002258]})
        
        mock_read_csv.side_effect = [data_1, data_2, data_3]

        # Call the function and verify the results
        rankings = get_multiplex_rankings("fake_directory")
        self.assertEqual(len(rankings), 3)  # Ensure three DataFrames are returned
        
        # Verify that the returned DataFrames match the expected DataFrames
        expected_dfs = [data_1, data_2, data_3]
        for df, expected in zip(rankings, expected_dfs):
            pd.testing.assert_frame_equal(df, expected)

if __name__ == "__main__":
    unittest.main()
