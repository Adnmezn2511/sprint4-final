import os
import tempfile
import unittest
import pandas as pd
from app.graph.multiplex_graph import MultiplexGraph


def _write_sif(directory, lines):
    path = os.path.join(directory, "ranking.sif")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


def _write_ranking(directory, rows):
    path = os.path.join(directory, "ranking.csv")
    df = pd.DataFrame(rows)
    df.to_csv(path, sep="\t", index=False)
    return path


class TestMultiplexGraphLoadSif(unittest.TestCase):
    """Tests de non-régression pour le chargement du SIF dans MultiplexGraph."""

    def test_load_valid_multiplex_relation(self):
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, ["A\tmultiplex/1/genes.tsv\tB"])
            g = MultiplexGraph(sif)
            graph, layers = g.get_graph()
            self.assertEqual(len(graph.nodes), 2)
            self.assertIn("1", layers)

    def test_load_bipartite_relation(self):
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, ["A\tbipartite/1_2.tsv\tX"])
            g = MultiplexGraph(sif)
            graph, layers = g.get_graph()
            self.assertEqual(len(graph.nodes), 2)
            self.assertIn("1", layers)
            self.assertIn("2", layers)

    def test_empty_sif_no_nodes(self):
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, [])
            g = MultiplexGraph(sif)
            graph, layers = g.get_graph()
            self.assertEqual(len(graph.nodes), 0)

    def test_malformed_line_skipped(self):
        """Ligne à 2 colonnes → ignorée, pas d'exception."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, ["A\tmultiplex/1/genes.tsv\tB", "MALFORMED"])
            g = MultiplexGraph(sif)
            graph, _ = g.get_graph()
            # Seule la ligne valide est chargée
            self.assertEqual(len(graph.nodes), 2)

    def test_comment_lines_skipped(self):
        """Lignes commençant par # → ignorées."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, ["# This is a comment", "A\tmultiplex/1/genes.tsv\tB"])
            g = MultiplexGraph(sif)
            graph, _ = g.get_graph()
            self.assertEqual(len(graph.nodes), 2)

    def test_layers_sorted_numerically(self):
        """Les couches sont triées numériquement, pas lexicographiquement."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, [
                "A\tmultiplex/10/genes.tsv\tB",
                "C\tmultiplex/2/diseases.tsv\tD",
            ])
            g = MultiplexGraph(sif)
            _, layers = g.get_graph()
            self.assertEqual(layers, sorted(layers, key=int))

    def test_nodes_have_layer_attribute(self):
        """Chaque nœud a un attribut 'layer'."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, ["A\tmultiplex/1/genes.tsv\tB"])
            g = MultiplexGraph(sif)
            graph, _ = g.get_graph()
            for node, data in graph.nodes(data=True):
                self.assertIn("layer", data)

    def test_nodes_have_score_zero_without_ranking(self):
        """Sans ranking_file → score de chaque nœud = 0."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, ["A\tmultiplex/1/genes.tsv\tB"])
            g = MultiplexGraph(sif)
            graph, _ = g.get_graph()
            for _, data in graph.nodes(data=True):
                self.assertEqual(data["score"], 0)


class TestMultiplexGraphWithRanking(unittest.TestCase):
    """Tests avec un fichier ranking CSV."""

    def test_scores_loaded_from_ranking(self):
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, ["A\tmultiplex/1/genes.tsv\tB"])
            ranking = _write_ranking(tmp, [
                {"multiplex": "1", "node": "A", "layer": "multiplex/1/genes.tsv", "score": 0.9},
                {"multiplex": "1", "node": "B", "layer": "multiplex/1/genes.tsv", "score": 0.5},
            ])
            g = MultiplexGraph(sif, ranking)
            graph, _ = g.get_graph()
            scores = {data["label"]: data["score"] for _, data in graph.nodes(data=True)}
            self.assertAlmostEqual(scores["A"], 0.9)
            self.assertAlmostEqual(scores["B"], 0.5)

    def test_node_not_in_ranking_gets_score_zero(self):
        """Nœud absent du ranking → score = 0."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, ["A\tmultiplex/1/genes.tsv\tC"])
            ranking = _write_ranking(tmp, [
                {"multiplex": "1", "node": "A", "layer": "multiplex/1/genes.tsv", "score": 0.8},
            ])
            g = MultiplexGraph(sif, ranking)
            graph, _ = g.get_graph()
            scores = {data["label"]: data["score"] for _, data in graph.nodes(data=True)}
            self.assertEqual(scores.get("C", 0), 0)

    def test_duplicate_nodes_share_same_score(self):
        """Même nœud dans plusieurs arêtes → score cohérent."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = _write_sif(tmp, [
                "A\tmultiplex/1/genes.tsv\tB",
                "A\tmultiplex/1/genes.tsv\tC",
            ])
            ranking = _write_ranking(tmp, [
                {"multiplex": "1", "node": "A", "layer": "multiplex/1/genes.tsv", "score": 0.7},
                {"multiplex": "1", "node": "B", "layer": "multiplex/1/genes.tsv", "score": 0.3},
                {"multiplex": "1", "node": "C", "layer": "multiplex/1/genes.tsv", "score": 0.2},
            ])
            g = MultiplexGraph(sif, ranking)
            graph, _ = g.get_graph()
            # A n'apparaît qu'une fois dans le graphe
            a_nodes = [(n, d) for n, d in graph.nodes(data=True) if d["label"] == "A"]
            self.assertEqual(len(a_nodes), 1)
            self.assertAlmostEqual(a_nodes[0][1]["score"], 0.7)


if __name__ == "__main__":
    unittest.main()