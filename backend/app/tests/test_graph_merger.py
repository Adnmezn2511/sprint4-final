import unittest
import networkx as nx

from app.graph.graph_merger import merge_patient_graphs


def _make_patient_graph(nodes_data, edges_data, layers):
    """Helper: builds a nx.Graph from node/edge specs."""
    G = nx.Graph()
    for node_id, attrs in nodes_data:
        G.add_node(node_id, **attrs)
    for u, v, attrs in edges_data:
        G.add_edge(u, v, **attrs)
    return G, layers


class TestMergePatientGraphsSinglePatient(unittest.TestCase):
    """Tests with a single patient — verifies freq=1 everywhere."""

    def setUp(self):
        node_a = (("GeneA", "1"), {"label": "GeneA", "layer": "1", "score": 0.8})
        node_b = (("GeneB", "1"), {"label": "GeneB", "layer": "1", "score": 0.5})
        edge = (("GeneA", "1"), ("GeneB", "1"), {"relation": "ppi"})
        G, layers = _make_patient_graph([node_a, node_b], [edge], ["1"])
        self.result, self.merged_layers = merge_patient_graphs(
            {"P1": (G, layers, ["GeneA"])}
        )

    def test_node_count(self):
        self.assertEqual(self.result.number_of_nodes(), 2)

    def test_edge_count(self):
        self.assertEqual(self.result.number_of_edges(), 1)

    def test_node_freq_is_one(self):
        for n in self.result.nodes():
            self.assertEqual(self.result.nodes[n]["freq"], 1)

    def test_edge_freq_is_one(self):
        for u, v in self.result.edges():
            self.assertEqual(self.result.edges[u, v]["freq"], 1)

    def test_seed_tracked(self):
        node = ("GeneA", "1")
        self.assertIn("P1", self.result.nodes[node]["patient_seeds"])

    def test_non_seed_not_tracked(self):
        node = ("GeneB", "1")
        self.assertNotIn("P1", self.result.nodes[node]["patient_seeds"])

    def test_score_preserved(self):
        node = ("GeneA", "1")
        self.assertAlmostEqual(self.result.nodes[node]["score"], 0.8)

    def test_mean_score_equals_score_for_one_patient(self):
        node = ("GeneA", "1")
        self.assertAlmostEqual(
            self.result.nodes[node]["mean_score"],
            self.result.nodes[node]["score"]
        )

    def test_layers_sorted(self):
        self.assertEqual(self.merged_layers, ["1"])


class TestMergePatientGraphsTwoPatients(unittest.TestCase):
    """Tests with two patients sharing a common node."""

    def setUp(self):
        # Patient 1: GeneA (score 0.8), GeneB (score 0.5), edge A-B
        node_a = (("GeneA", "1"), {"label": "GeneA", "layer": "1", "score": 0.8})
        node_b = (("GeneB", "1"), {"label": "GeneB", "layer": "1", "score": 0.5})
        edge_ab = (("GeneA", "1"), ("GeneB", "1"), {"relation": "ppi"})
        G1, layers1 = _make_patient_graph([node_a, node_b], [edge_ab], ["1"])

        # Patient 2: GeneA (score 0.6), GeneC (score 0.9), edge A-C
        node_a2 = (("GeneA", "1"), {"label": "GeneA", "layer": "1", "score": 0.6})
        node_c = (("GeneC", "2"), {"label": "GeneC", "layer": "2", "score": 0.9})
        edge_ac = (("GeneA", "1"), ("GeneC", "2"), {"relation": "disease"})
        G2, layers2 = _make_patient_graph([node_a2, node_c], [edge_ac], ["1", "2"])

        self.result, self.merged_layers = merge_patient_graphs({
            "P1": (G1, layers1, ["GeneA"]),
            "P2": (G2, layers2, ["GeneA"]),
        })

    def test_shared_node_freq(self):
        """GeneA appears in both patients → freq=2."""
        node = ("GeneA", "1")
        self.assertEqual(self.result.nodes[node]["freq"], 2)

    def test_exclusive_node_freq(self):
        """GeneB and GeneC appear in one patient each → freq=1."""
        self.assertEqual(self.result.nodes[("GeneB", "1")]["freq"], 1)
        self.assertEqual(self.result.nodes[("GeneC", "2")]["freq"], 1)

    def test_shared_node_max_score(self):
        """max_score for GeneA should be max(0.8, 0.6) = 0.8."""
        node = ("GeneA", "1")
        self.assertAlmostEqual(self.result.nodes[node]["max_score"], 0.8)
        self.assertAlmostEqual(self.result.nodes[node]["score"], 0.8)

    def test_shared_node_mean_score(self):
        """mean_score for GeneA = (0.8 + 0.6) / 2 = 0.7."""
        node = ("GeneA", "1")
        self.assertAlmostEqual(self.result.nodes[node]["mean_score"], 0.7)

    def test_patient_scores_dict(self):
        node = ("GeneA", "1")
        ps = self.result.nodes[node]["patient_scores"]
        self.assertAlmostEqual(ps["P1"], 0.8)
        self.assertAlmostEqual(ps["P2"], 0.6)

    def test_total_node_count(self):
        # GeneA, GeneB, GeneC → 3 nodes
        self.assertEqual(self.result.number_of_nodes(), 3)

    def test_total_edge_count(self):
        # A-B (P1 only) and A-C (P2 only) → 2 edges
        self.assertEqual(self.result.number_of_edges(), 2)

    def test_exclusive_edge_freq(self):
        edge_ab = self.result.edges[("GeneA", "1"), ("GeneB", "1")]
        self.assertEqual(edge_ab["freq"], 1)

    def test_layers_union_sorted(self):
        self.assertEqual(self.merged_layers, ["1", "2"])

    def test_seed_tracking_both_patients(self):
        """GeneA is a seed for both patients."""
        node = ("GeneA", "1")
        seeds = self.result.nodes[node]["patient_seeds"]
        self.assertIn("P1", seeds)
        self.assertIn("P2", seeds)


class TestMergePatientGraphsSharedEdge(unittest.TestCase):
    """Tests where two patients share the same edge."""

    def setUp(self):
        node_a = (("GeneA", "1"), {"label": "GeneA", "layer": "1", "score": 0.5})
        node_b = (("GeneB", "1"), {"label": "GeneB", "layer": "1", "score": 0.3})
        edge = (("GeneA", "1"), ("GeneB", "1"), {"relation": "ppi"})

        G1, layers1 = _make_patient_graph([node_a, node_b], [edge], ["1"])
        G2, layers2 = _make_patient_graph([node_a, node_b], [edge], ["1"])

        self.result, _ = merge_patient_graphs({
            "P1": (G1, layers1, []),
            "P2": (G2, layers2, []),
        })

    def test_shared_edge_freq(self):
        edge = self.result.edges[("GeneA", "1"), ("GeneB", "1")]
        self.assertEqual(edge["freq"], 2)

    def test_shared_edge_patients_set(self):
        edge = self.result.edges[("GeneA", "1"), ("GeneB", "1")]
        self.assertIn("P1", edge["patients"])
        self.assertIn("P2", edge["patients"])


if __name__ == "__main__":
    unittest.main()
