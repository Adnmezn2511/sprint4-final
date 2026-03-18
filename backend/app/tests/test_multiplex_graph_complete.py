import os
import tempfile
import unittest
from app.graph.multiplex_graph import MultiplexGraph
import pandas as pd


def write_sif(path, lines):
    with open(path, "w") as f:
        f.write("\n".join(lines))


def write_ranking(path, rows):
    """
    Format exact du ranking_final.csv produit par multixrank :
    colonnes: multiplex (str id), node, layer (chemin complet ex: multiplex/1/genes.tsv), score
    Le mapping dans MultiplexGraph utilise la clé (node, multiplex_id).
    """
    df = pd.DataFrame(rows)
    df.to_csv(path, sep='\t', index=False)


class TestMultiplexGraphMissingFiles(unittest.TestCase):

    def test_missing_sif_raises(self):
        with self.assertRaises(Exception):
            MultiplexGraph("/nonexistent/file.sif", "/nonexistent/ranking.csv")


class TestMultiplexGraphGetGraph(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.sif = os.path.join(self.tmp.name, "ranking.sif")
        self.ranking = os.path.join(self.tmp.name, "ranking.csv")

    def tearDown(self):
        self.tmp.cleanup()

    def test_get_graph_returns_graph_and_layers(self):
        write_sif(self.sif, [
            "GeneA\tmultiplex/1/genes.tsv\tGeneB",
            "GeneA\tbipartite/1_2.tsv\tDisease1",
        ])
        write_ranking(self.ranking, [
            {"multiplex": "1", "node": "GeneA", "layer": "multiplex/1/genes.tsv", "score": 0.9},
            {"multiplex": "1", "node": "GeneB", "layer": "multiplex/1/genes.tsv", "score": 0.5},
            {"multiplex": "2", "node": "Disease1", "layer": "multiplex/2/diseases.tsv", "score": 0.3},
        ])
        mg = MultiplexGraph(self.sif, self.ranking)
        G, layers = mg.get_graph()
        self.assertIsNotNone(G)
        self.assertIsInstance(layers, list)
        self.assertGreater(len(G.nodes()), 0)

    def test_nodes_have_score(self):
        write_sif(self.sif, ["GeneA\tmultiplex/1/genes.tsv\tGeneB"])
        write_ranking(self.ranking, [
            {"multiplex": "1", "node": "GeneA", "layer": "multiplex/1/genes.tsv", "score": 0.9},
            {"multiplex": "1", "node": "GeneB", "layer": "multiplex/1/genes.tsv", "score": 0.4},
        ])
        mg = MultiplexGraph(self.sif, self.ranking)
        G, _ = mg.get_graph()
        for n in G.nodes():
            self.assertIn("score", G.nodes[n])

    def test_nodes_have_layer(self):
        write_sif(self.sif, ["GeneA\tmultiplex/1/genes.tsv\tGeneB"])
        write_ranking(self.ranking, [
            {"multiplex": "1", "node": "GeneA", "layer": "multiplex/1/genes.tsv", "score": 0.9},
            {"multiplex": "1", "node": "GeneB", "layer": "multiplex/1/genes.tsv", "score": 0.4},
        ])
        mg = MultiplexGraph(self.sif, self.ranking)
        G, _ = mg.get_graph()
        for n in G.nodes():
            self.assertIn("layer", G.nodes[n])

    def test_empty_sif(self):
        write_sif(self.sif, [])
        write_ranking(self.ranking, [
            {"multiplex": "1", "node": "GeneA", "layer": "multiplex/1/genes.tsv", "score": 0.9},
        ])
        mg = MultiplexGraph(self.sif, self.ranking)
        G, layers = mg.get_graph()
        self.assertEqual(len(G.nodes()), 0)

    def test_layers_sorted(self):
        write_sif(self.sif, [
            "GeneA\tmultiplex/2/genes.tsv\tGeneB",
            "GeneA\tmultiplex/1/genes.tsv\tGeneC",
        ])
        write_ranking(self.ranking, [
            {"multiplex": "2", "node": "GeneB", "layer": "multiplex/2/genes.tsv", "score": 0.5},
            {"multiplex": "1", "node": "GeneA", "layer": "multiplex/1/genes.tsv", "score": 0.9},
            {"multiplex": "1", "node": "GeneC", "layer": "multiplex/1/genes.tsv", "score": 0.3},
        ])
        mg = MultiplexGraph(self.sif, self.ranking)
        G, layers = mg.get_graph()
        self.assertEqual(layers, sorted(layers, key=int))


if __name__ == "__main__":
    unittest.main()