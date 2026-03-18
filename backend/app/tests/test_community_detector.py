import unittest
import networkx as nx
from app.graph.community_detector import CommunityDetector


def _build_two_cliques() -> nx.Graph:
    """Deux cliques de 4 nœuds reliées par une seule arête → 2 communautés attendues."""
    G = nx.Graph()
    # clique A : 0-1-2-3
    G.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    # clique B : 4-5-6-7
    G.add_edges_from([(4, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7)])
    # pont entre les deux cliques
    G.add_edge(3, 4)
    return G


def _build_star() -> nx.Graph:
    """Graphe étoile : un nœud central relié à 5 feuilles."""
    return nx.star_graph(5)


def _build_directed() -> nx.DiGraph:
    """Graphe dirigé avec deux cycles distincts."""
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])   # cycle A
    G.add_edges_from([(3, 4), (4, 5), (5, 3)])   # cycle B
    G.add_edge(2, 3)                              # pont
    return G


# ── Tests d'initialisation ───────────────────────────────────────────────────

class TestCommunityDetectorInit(unittest.TestCase):

    def test_valid_init(self):
        G = _build_two_cliques()
        cd = CommunityDetector(G, algorithm="greedy")
        self.assertEqual(cd.algorithm, "greedy")

    def test_default_algorithm_is_louvain(self):
        G = _build_two_cliques()
        cd = CommunityDetector(G)
        self.assertEqual(cd.algorithm, "louvain")

    def test_invalid_algorithm_raises(self):
        G = _build_two_cliques()
        with self.assertRaises(ValueError) as ctx:
            CommunityDetector(G, algorithm="unknown_algo")
        self.assertIn("non supporté", str(ctx.exception))

    def test_empty_graph_raises(self):
        G = nx.Graph()
        with self.assertRaises(ValueError) as ctx:
            CommunityDetector(G)
        self.assertIn("vide", str(ctx.exception))

    def test_none_graph_raises(self):
        with self.assertRaises((ValueError, AttributeError)):
            CommunityDetector(None)


# ── Tests algorithme "greedy" ────────────────────────────────────────────────

class TestGreedyModularity(unittest.TestCase):

    def test_two_cliques_gives_two_communities(self):
        G = _build_two_cliques()
        cd = CommunityDetector(G, algorithm="greedy")
        result = cd.detect()
        self.assertEqual(len(result), 2)

    def test_all_nodes_covered(self):
        G = _build_two_cliques()
        cd = CommunityDetector(G, algorithm="greedy")
        result = cd.detect()
        covered = {n for comm in result for n in comm}
        self.assertEqual(covered, set(G.nodes()))

    def test_returns_list_of_lists(self):
        G = _build_star()
        cd = CommunityDetector(G, algorithm="greedy")
        result = cd.detect()
        self.assertIsInstance(result, list)
        for comm in result:
            self.assertIsInstance(comm, list)

    def test_directed_input_converted(self):
        """greedy doit fonctionner même avec un DiGraph en entrée."""
        G = _build_directed()
        cd = CommunityDetector(G, algorithm="greedy")
        result = cd.detect()
        self.assertGreater(len(result), 0)


# ── Tests algorithme "louvain" ───────────────────────────────────────────────

class TestLouvain(unittest.TestCase):

    def test_two_cliques_gives_two_communities(self):
        G = _build_two_cliques()
        cd = CommunityDetector(G, algorithm="louvain")
        result = cd.detect()
        self.assertEqual(len(result), 2)

    def test_all_nodes_covered(self):
        G = _build_two_cliques()
        cd = CommunityDetector(G, algorithm="louvain")
        result = cd.detect()
        covered = {n for comm in result for n in comm}
        self.assertEqual(covered, set(G.nodes()))

    def test_returns_list_of_lists(self):
        G = _build_star()
        cd = CommunityDetector(G, algorithm="louvain")
        result = cd.detect()
        self.assertIsInstance(result, list)

    def test_directed_converted_to_undirected(self):
        G = _build_directed()
        cd = CommunityDetector(G, algorithm="louvain")
        result = cd.detect()
        self.assertGreater(len(result), 0)


# ── Tests algorithme "connected" ─────────────────────────────────────────────

class TestConnectedComponents(unittest.TestCase):

    def test_two_disconnected_components(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])   # composante 1
        G.add_edges_from([(3, 4)])            # composante 2
        cd = CommunityDetector(G, algorithm="connected")
        result = cd.detect()
        self.assertEqual(len(result), 2)

    def test_fully_connected_graph_one_component(self):
        G = nx.complete_graph(6)
        cd = CommunityDetector(G, algorithm="connected")
        result = cd.detect()
        self.assertEqual(len(result), 1)

    def test_all_nodes_covered(self):
        G = _build_two_cliques()
        cd = CommunityDetector(G, algorithm="connected")
        result = cd.detect()
        covered = {n for comm in result for n in comm}
        self.assertEqual(covered, set(G.nodes()))


# ── Tests algorithme "scc" ───────────────────────────────────────────────────

class TestStronglyConnectedComponents(unittest.TestCase):

    def test_two_cycles_gives_three_or_more_sccs(self):
        """Deux cycles + pont → cycles = SCC, nœud pont éventuellement seul."""
        G = _build_directed()
        cd = CommunityDetector(G, algorithm="scc")
        result = cd.detect()
        self.assertGreaterEqual(len(result), 2)

    def test_all_nodes_covered(self):
        G = _build_directed()
        cd = CommunityDetector(G, algorithm="scc")
        result = cd.detect()
        covered = {n for comm in result for n in comm}
        self.assertEqual(covered, set(G.nodes()))

    def test_undirected_input_converted(self):
        """scc doit fonctionner même avec un Graph non dirigé en entrée."""
        G = _build_two_cliques()
        cd = CommunityDetector(G, algorithm="scc")
        result = cd.detect()
        self.assertGreater(len(result), 0)


# ── Tests utilitaire communities_to_dict ─────────────────────────────────────

class TestCommunitiesToDict(unittest.TestCase):

    def test_structure_keys(self):
        communities = [[0, 1, 2], [3, 4]]
        result = CommunityDetector.communities_to_dict(communities)
        self.assertIn("nb_communities", result)
        self.assertIn("communities", result)

    def test_nb_communities_correct(self):
        communities = [[0, 1], [2, 3], [4]]
        result = CommunityDetector.communities_to_dict(communities)
        self.assertEqual(result["nb_communities"], 3)

    def test_community_entries_have_id_size_nodes(self):
        communities = [[10, 20, 30], [40]]
        result = CommunityDetector.communities_to_dict(communities)
        for entry in result["communities"]:
            self.assertIn("id", entry)
            self.assertIn("size", entry)
            self.assertIn("nodes", entry)

    def test_community_size_matches_nodes_length(self):
        communities = [[0, 1, 2, 3], [4, 5]]
        result = CommunityDetector.communities_to_dict(communities)
        for entry in result["communities"]:
            self.assertEqual(entry["size"], len(entry["nodes"]))

    def test_nodes_are_strings(self):
        """Les nœuds doivent être des chaînes (JSON-ready)."""
        communities = [[(0, "1"), (1, "1")], [(2, "2")]]
        result = CommunityDetector.communities_to_dict(communities)
        for entry in result["communities"]:
            for node in entry["nodes"]:
                self.assertIsInstance(node, str)

    def test_empty_communities_list(self):
        result = CommunityDetector.communities_to_dict([])
        self.assertEqual(result["nb_communities"], 0)
        self.assertEqual(result["communities"], [])


if __name__ == "__main__":
    unittest.main()