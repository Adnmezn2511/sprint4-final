import unittest
import os
import tempfile
import pandas as pd
from app.itRWR.ranking_utils import (
    get_multiplex_rankings_mem,
    update_layer_max_scores_vec,
    update_layer_max_scores,
    write_normalized_scores,
    get_ranking_df_from_max_scores,
)


def _make_ranking_df(multiplex_ids=(1, 2)):
    """Helper : construit un DataFrame ranking réaliste."""
    rows = []
    for mid in multiplex_ids:
        rows += [
            {"multiplex": mid, "node": f"N{mid}_A", "layer": f"multiplex/{mid}/genes.tsv", "score": 0.9},
            {"multiplex": mid, "node": f"N{mid}_B", "layer": f"multiplex/{mid}/genes.tsv", "score": 0.5},
        ]
    return pd.DataFrame(rows)


class TestGetMultiplexRankingsMem(unittest.TestCase):
    """Tests pour get_multiplex_rankings_mem."""

    def test_returns_one_df_per_multiplex(self):
        df = _make_ranking_df(multiplex_ids=(1, 2))
        result = get_multiplex_rankings_mem(df)
        self.assertEqual(len(result), 2)

    def test_each_result_contains_correct_multiplex(self):
        df = _make_ranking_df(multiplex_ids=(1, 2, 3))
        result = get_multiplex_rankings_mem(df)
        multiplex_values = sorted([r["multiplex"].iloc[0] for r in result])
        self.assertEqual(multiplex_values, [1, 2, 3])

    def test_export_files_created_when_outdir_given(self):
        df = _make_ranking_df(multiplex_ids=(1, 2))
        with tempfile.TemporaryDirectory() as tmp:
            get_multiplex_rankings_mem(df, outdir=tmp)
            files = os.listdir(tmp)
            self.assertIn("multiplex_1.tsv", files)
            self.assertIn("multiplex_2.tsv", files)

    def test_no_file_created_without_outdir(self):
        df = _make_ranking_df(multiplex_ids=(1,))
        with tempfile.TemporaryDirectory() as tmp:
            # On ne passe PAS outdir, les fichiers ne doivent pas apparaître dans tmp
            get_multiplex_rankings_mem(df, outdir=None)
            self.assertEqual(os.listdir(tmp), [])

    def test_single_multiplex(self):
        df = _make_ranking_df(multiplex_ids=(42,))
        result = get_multiplex_rankings_mem(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["multiplex"].iloc[0], 42)

    def test_exported_file_content_matches_dataframe(self):
        df = _make_ranking_df(multiplex_ids=(1,))
        with tempfile.TemporaryDirectory() as tmp:
            get_multiplex_rankings_mem(df, outdir=tmp)
            loaded = pd.read_csv(os.path.join(tmp, "multiplex_1.tsv"), sep="\t")
            self.assertIn("node", loaded.columns)
            self.assertIn("score", loaded.columns)


class TestUpdateLayerMaxScoresVec(unittest.TestCase):
    """Tests pour update_layer_max_scores_vec (version vectorisée)."""

    def _make_ranking(self, nodes_scores):
        """nodes_scores : liste de (node, score, layer)"""
        return pd.DataFrame([
            {"multiplex": 1, "node": n, "layer": l, "score": s}
            for n, s, l in nodes_scores
        ])

    def test_layer_keys_created(self):
        ranking = self._make_ranking([("A", 0.9, "multiplex/1/genes.tsv")])
        layer_max_scores = {}
        update_layer_max_scores_vec(ranking, [ranking], layer_max_scores)
        self.assertIn("multiplex/1/genes.tsv", layer_max_scores)

    def test_max_score_correct(self):
        ranking = self._make_ranking([
            ("A", 0.9, "multiplex/1/genes.tsv"),
            ("B", 0.3, "multiplex/1/genes.tsv"),
        ])
        layer_max_scores = {}
        update_layer_max_scores_vec(ranking, [ranking], layer_max_scores)
        scores = layer_max_scores["multiplex/1/genes.tsv"]
        self.assertAlmostEqual(scores["A"], 0.9)
        self.assertAlmostEqual(scores["B"], 0.3)

    def test_repeated_call_keeps_max(self):
        """Deux appels successifs → le max est conservé, pas écrasé."""
        r1 = self._make_ranking([("A", 0.9, "multiplex/1/genes.tsv")])
        r2 = self._make_ranking([("A", 0.3, "multiplex/1/genes.tsv")])
        layer_max_scores = {}
        update_layer_max_scores_vec(r1, [r1], layer_max_scores)
        update_layer_max_scores_vec(r2, [r2], layer_max_scores)
        self.assertAlmostEqual(layer_max_scores["multiplex/1/genes.tsv"]["A"], 0.9)

    def test_multiple_layers(self):
        ranking = pd.DataFrame([
            {"multiplex": 1, "node": "A", "layer": "multiplex/1/genes.tsv", "score": 0.8},
            {"multiplex": 2, "node": "X", "layer": "multiplex/2/diseases.tsv", "score": 0.6},
        ])
        layer_max_scores = {}
        update_layer_max_scores_vec(ranking, [ranking], layer_max_scores)
        self.assertIn("multiplex/1/genes.tsv", layer_max_scores)
        self.assertIn("multiplex/2/diseases.tsv", layer_max_scores)

    def test_vec_equals_non_vec(self):
        """La version vectorisée doit produire le même résultat que la version iterrows."""
        ranking = pd.DataFrame([
            {"multiplex": 1, "node": "A", "layer": "multiplex/1/g.tsv", "score": 0.7},
            {"multiplex": 1, "node": "B", "layer": "multiplex/1/g.tsv", "score": 0.4},
        ])
        ranking_files = [ranking]

        scores_vec = {}
        update_layer_max_scores_vec(ranking, ranking_files, scores_vec)

        scores_iter = {}
        update_layer_max_scores(ranking, ranking_files, scores_iter)

        self.assertEqual(sorted(scores_vec.keys()), sorted(scores_iter.keys()))
        for layer in scores_vec:
            for node in scores_vec[layer]:
                self.assertAlmostEqual(
                    scores_vec[layer][node],
                    scores_iter[layer][node],
                    places=7,
                    msg=f"Divergence pour layer={layer} node={node}"
                )


class TestWriteNormalizedScores(unittest.TestCase):
    """Tests pour write_normalized_scores."""

    def test_files_created(self):
        layer_max_scores = {"multiplex/1/genes.tsv": {"A": 0.9, "B": 0.45}}
        with tempfile.TemporaryDirectory() as tmp:
            write_normalized_scores(tmp, layer_max_scores)
            files = os.listdir(tmp)
            self.assertTrue(any("max_scores.tsv" in f for f in files))

    def test_normalization_max_node_equals_one(self):
        layer_max_scores = {"multiplex/1/genes.tsv": {"A": 1.0, "B": 0.5}}
        with tempfile.TemporaryDirectory() as tmp:
            write_normalized_scores(tmp, layer_max_scores)
            tsv = os.path.join(tmp, "1_max_scores.tsv")
            df = pd.read_csv(tsv, sep="\t")
            a_score = df.loc[df["node"] == "A", "score"].values[0]
            b_score = df.loc[df["node"] == "B", "score"].values[0]
            self.assertAlmostEqual(a_score, 1.0)
            self.assertAlmostEqual(b_score, 0.5)

    def test_zero_max_score_no_division_by_zero(self):
        """Tous les scores à 0 → pas de ZeroDivisionError."""
        layer_max_scores = {"multiplex/1/genes.tsv": {"A": 0.0, "B": 0.0}}
        with tempfile.TemporaryDirectory() as tmp:
            write_normalized_scores(tmp, layer_max_scores)

    def test_output_has_correct_columns(self):
        layer_max_scores = {"multiplex/1/genes.tsv": {"A": 0.8}}
        with tempfile.TemporaryDirectory() as tmp:
            write_normalized_scores(tmp, layer_max_scores)
            tsv = os.path.join(tmp, "1_max_scores.tsv")
            df = pd.read_csv(tsv, sep="\t")
            for col in ["multiplex", "node", "layer", "score"]:
                self.assertIn(col, df.columns)

    def test_multiple_layers_multiple_files(self):
        layer_max_scores = {
            "multiplex/1/genes.tsv": {"A": 0.9},
            "multiplex/2/diseases.tsv": {"X": 0.7},
        }
        with tempfile.TemporaryDirectory() as tmp:
            write_normalized_scores(tmp, layer_max_scores)
            files = os.listdir(tmp)
            self.assertEqual(len(files), 2)

    def test_empty_layer_max_scores_no_files_created(self):
        """Dictionnaire vide → aucun fichier créé (sauf le dossier)."""
        with tempfile.TemporaryDirectory() as tmp:
            write_normalized_scores(tmp, {})
            files = os.listdir(tmp)
            self.assertEqual(files, [])


class TestGetRankingDfFromMaxScores(unittest.TestCase):
    """Tests pour get_ranking_df_from_max_scores."""

    def _create_scores_file(self, directory, filename, rows):
        path = os.path.join(directory, filename)
        with open(path, "w") as f:
            f.write("multiplex\tnode\tlayer\tscore\n")
            for r in rows:
                f.write("\t".join(map(str, r)) + "\n")
        return path

    def test_returns_top_n_nodes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._create_scores_file(tmp, "1_max_scores.tsv", [
                (1, "A", "l1", 0.9),
                (1, "B", "l1", 0.8),
                (1, "C", "l1", 0.7),
                (1, "D", "l1", 0.6),
            ])
            df = get_ranking_df_from_max_scores(tmp, nb_nodes_per_layer=2)
            self.assertEqual(len(df), 2)

    def test_top_node_is_highest_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._create_scores_file(tmp, "1_max_scores.tsv", [
                (1, "A", "l1", 0.9),
                (1, "B", "l1", 0.1),
            ])
            df = get_ranking_df_from_max_scores(tmp, nb_nodes_per_layer=1)
            self.assertEqual(df.iloc[0]["node"], "A")

    def test_empty_directory_returns_empty_df(self):
        with tempfile.TemporaryDirectory() as tmp:
            df = get_ranking_df_from_max_scores(tmp, nb_nodes_per_layer=10)
            self.assertTrue(df.empty)

    def test_multiple_files_concatenated(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._create_scores_file(tmp, "1_max_scores.tsv", [(1, "A", "l1", 0.9)])
            self._create_scores_file(tmp, "2_max_scores.tsv", [(2, "X", "l2", 0.8)])
            df = get_ranking_df_from_max_scores(tmp, nb_nodes_per_layer=5)
            self.assertEqual(len(df), 2)
            nodes = set(df["node"].values)
            self.assertIn("A", nodes)
            self.assertIn("X", nodes)

    def test_nb_nodes_larger_than_available(self):
        """nb_nodes_per_layer > nb de nœuds → tous retournés sans erreur."""
        with tempfile.TemporaryDirectory() as tmp:
            self._create_scores_file(tmp, "1_max_scores.tsv", [
                (1, "A", "l1", 0.9),
                (1, "B", "l1", 0.5),
            ])
            df = get_ranking_df_from_max_scores(tmp, nb_nodes_per_layer=100)
            self.assertEqual(len(df), 2)


if __name__ == "__main__":
    unittest.main()