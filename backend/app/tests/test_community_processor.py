import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
from app.itRWR.communityProcessor import CommunityProcessor


def make_processor(path, out_folder, nb_iter=1, nb_nodes=5):
    return CommunityProcessor(
        path=path,
        config_file="config.yml",
        out_folder=out_folder,
        seeds_file="seeds.txt",
        nb_iterations=nb_iter,
        nb_nodes_per_layer=nb_nodes
    )


class TestCommunityProcessorInit(unittest.TestCase):

    def test_init_attributes(self):
        cp = CommunityProcessor(
            path="/some/path",
            config_file="config.yml",
            out_folder="result_1",
            seeds_file="seeds.txt",
            nb_iterations=3,
            nb_nodes_per_layer=10
        )
        self.assertEqual(cp.path, "/some/path")
        self.assertEqual(cp.config_file, "config.yml")
        self.assertEqual(cp.out_folder, "result_1")
        self.assertEqual(cp.seeds_file, "seeds.txt")
        self.assertEqual(cp.nb_iterations, 3)
        self.assertEqual(cp.nb_nodes_per_layer, 10)
        self.assertEqual(cp.layer_max_scores, {})
        self.assertEqual(cp.added_nodes, set())


class TestCommunityProcessorRun(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = self.tmp.name
        self.out_folder = os.path.join(self.path, "result_1")
        os.makedirs(self.out_folder)
        seeds_path = os.path.join(self.out_folder, "seeds.txt")
        with open(seeds_path, "w") as f:
            f.write("GeneA\nGeneB\n")
        config_path = os.path.join(self.out_folder, "config.yml")
        with open(config_path, "w") as f:
            f.write("seed: seeds.txt\neta: 0.5\nr: 0.7\n")

    def tearDown(self):
        self.tmp.cleanup()

    @patch("app.itRWR.communityProcessor.write_normalized_scores")
    @patch("app.itRWR.communityProcessor.get_ranking_df_from_max_scores")
    @patch("app.itRWR.communityProcessor.filter_sif_file")
    @patch("app.itRWR.communityProcessor.correct_sif_order")
    @patch("app.itRWR.communityProcessor.update_seeds_from_iteration")
    @patch("app.itRWR.communityProcessor.update_layer_max_scores_vec")
    @patch("app.itRWR.communityProcessor.get_multiplex_rankings_mem")
    @patch("app.itRWR.communityProcessor.write_seeds")
    @patch("app.itRWR.communityProcessor.read_seeds")
    @patch("app.itRWR.communityProcessor.write_config_file")
    @patch("subprocess.call")
    @patch("app.itRWR.communityProcessor.mxk.Multixrank")
    def test_run_one_iteration(
        self, mock_mxk, mock_subp, mock_wcf, mock_rs, mock_ws,
        mock_gmm, mock_ulmv, mock_usi, mock_csif, mock_fsif,
        mock_grdfms, mock_wns
    ):
        mock_rs.return_value = {"GeneA", "GeneB"}
        mock_multixrank = MagicMock()
        mock_mxk.return_value = mock_multixrank
        ranking_df = pd.DataFrame({"multiplex": ["m1"], "node": ["GeneA"], "layer": [1], "score": [0.9]})
        mock_multixrank.random_walk_rank.return_value = ranking_df
        mock_multixrank.write_ranking.return_value = ranking_df
        mock_gmm.return_value = {"m1": pd.DataFrame()}
        final_df = pd.DataFrame({"node": ["GeneA"], "score": [0.9]})
        mock_grdfms.return_value = final_df

        cp = make_processor(self.path, self.out_folder, nb_iter=1)
        cp.run()

        mock_wcf.assert_called_once()
        mock_rs.assert_called_once()
        mock_mxk.assert_called_once()
        mock_multixrank.random_walk_rank.assert_called_once()
        mock_wns.assert_called_once()

    @patch("app.itRWR.communityProcessor.write_normalized_scores")
    @patch("app.itRWR.communityProcessor.get_ranking_df_from_max_scores")
    @patch("app.itRWR.communityProcessor.filter_sif_file")
    @patch("app.itRWR.communityProcessor.correct_sif_order")
    @patch("app.itRWR.communityProcessor.update_seeds_from_iteration")
    @patch("app.itRWR.communityProcessor.update_layer_max_scores_vec")
    @patch("app.itRWR.communityProcessor.get_multiplex_rankings_mem")
    @patch("app.itRWR.communityProcessor.write_seeds")
    @patch("app.itRWR.communityProcessor.read_seeds")
    @patch("app.itRWR.communityProcessor.write_config_file")
    @patch("subprocess.call")
    @patch("app.itRWR.communityProcessor.mxk.Multixrank")
    def test_run_multiple_iterations(
        self, mock_mxk, mock_subp, mock_wcf, mock_rs, mock_ws,
        mock_gmm, mock_ulmv, mock_usi, mock_csif, mock_fsif,
        mock_grdfms, mock_wns
    ):
        mock_rs.return_value = {"GeneA"}
        mock_multixrank = MagicMock()
        mock_mxk.return_value = mock_multixrank
        ranking_df = pd.DataFrame({"multiplex": ["m1"], "node": ["GeneA"], "layer": [1], "score": [0.8]})
        mock_multixrank.random_walk_rank.return_value = ranking_df
        mock_multixrank.write_ranking.return_value = ranking_df
        mock_gmm.return_value = {}
        mock_grdfms.return_value = pd.DataFrame({"node": ["GeneA"], "score": [0.8]})

        cp = make_processor(self.path, self.out_folder, nb_iter=3)
        cp.run()

        self.assertEqual(mock_mxk.call_count, 3)
        self.assertEqual(mock_multixrank.random_walk_rank.call_count, 3)


if __name__ == "__main__":
    unittest.main()