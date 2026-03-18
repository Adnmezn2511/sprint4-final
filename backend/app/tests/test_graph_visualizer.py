import os
import tempfile
import unittest
import networkx as nx
from app.visualization.graph_visualizer import GraphVisualizer


def build_simple_graph():
    """
    Reproduit exactement la structure que MultiplexGraph crée :
    - nodes = tuples (label, layer_str)
    - layer = string numérique (ex: "1", "2")
    - relation = relation complète comme dans le SIF
    """
    G = nx.Graph()
    # nodes = (label, layer_str) comme dans MultiplexGraph._add_nodes_and_edges
    G.add_node(("GeneA", "1"), layer="1", label="GeneA", score=0.9)
    G.add_node(("GeneB", "1"), layer="1", label="GeneB", score=0.5)
    G.add_node(("Disease1", "2"), layer="2", label="Disease1", score=0.3)
    G.add_edge(("GeneA", "1"), ("GeneB", "1"), relation="multiplex/1/genes.tsv")
    G.add_edge(("GeneA", "1"), ("Disease1", "2"), relation="bipartite/1_2.tsv")
    return G, ["1", "2"]


class TestGraphVisualizerInit(unittest.TestCase):

    def test_init(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        self.assertEqual(viz.layers, layers)
        self.assertIsNotNone(viz.pos)
        self.assertIsNotNone(viz.edge_colors)

    def test_pos_contains_all_nodes(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        for n in G.nodes():
            self.assertIn(n, viz.pos)

    def test_edge_colors_per_layer(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        for layer in layers:
            self.assertIn(layer, viz.edge_colors)


class TestAddOpacity(unittest.TestCase):

    def test_hex_color(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        result = viz.add_opacity("#ff0000", 0.5)
        self.assertIn("rgba", result)
        self.assertIn("0.5", result)

    def test_rgb_color(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        result = viz.add_opacity("rgb(100, 200, 50)", 0.8)
        self.assertIn("rgba", result)
        self.assertIn("0.8", result)

    def test_unknown_color_returned_as_is(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        result = viz.add_opacity("blue", 0.5)
        self.assertEqual(result, "blue")


class TestLayeredLayout(unittest.TestCase):

    def test_layout_no_crash_empty_layer(self):
        G = nx.Graph()
        G.add_node(("A", "1"), layer="1", label="A", score=0.0)
        viz = GraphVisualizer(G, ["1", "2"])
        self.assertIn(("A", "1"), viz.pos)

    def test_layout_two_layers(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        self.assertEqual(len(viz.pos), len(G.nodes()))


class TestGenerateBackgroundShapes(unittest.TestCase):

    def test_returns_shapes_and_annotations(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        shapes, annotations, rects = viz.generate_background_shapes_and_annotations()
        self.assertIsInstance(shapes, list)
        self.assertIsInstance(annotations, list)
        self.assertIsInstance(rects, dict)

    def test_with_layer_names(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        layer_names = {"1": "Genes", "2": "Diseases"}
        shapes, annotations, _ = viz.generate_background_shapes_and_annotations(layer_names=layer_names)
        annotation_texts = [a["text"] for a in annotations]
        self.assertTrue(any("Genes" in t or "Diseases" in t for t in annotation_texts))


class TestGroupEdges(unittest.TestCase):

    def test_group_edges_returns_dicts(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        groups, labels, colors = viz.group_edges_by_interaction()
        self.assertIsInstance(groups, dict)
        self.assertIsInstance(labels, dict)
        self.assertIsInstance(colors, dict)

    def test_group_keys_match(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        groups, labels, colors = viz.group_edges_by_interaction()
        self.assertEqual(set(groups.keys()), set(labels.keys()))
        self.assertEqual(set(groups.keys()), set(colors.keys()))


class TestCreateNodeTrace(unittest.TestCase):

    def test_node_trace_created(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        trace = viz.create_node_trace()
        self.assertIsNotNone(trace)

    def test_node_trace_with_seeds(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        trace = viz.create_node_trace(seeds=["GeneA"])
        symbols = trace.marker.symbol
        self.assertIn("square", symbols)
        self.assertIn("circle", symbols)

    def test_node_trace_count(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        trace = viz.create_node_trace()
        self.assertEqual(len(trace.x), len(G.nodes()))


class TestCreateEdgeTraces(unittest.TestCase):

    def test_edge_traces_list(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        groups, labels, colors = viz.group_edges_by_interaction()
        traces = viz.create_edge_traces(groups, labels, colors)
        self.assertIsInstance(traces, list)
        self.assertGreater(len(traces), 0)


class TestCreateInteractiveGraph(unittest.TestCase):

    def test_create_interactive_graph_returns_figure(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "graph.html")
            fig = viz.create_interactive_graph(out, seeds=["GeneA"])
            self.assertIsNotNone(fig)
            self.assertTrue(os.path.exists(out))

    def test_create_interactive_graph_with_params(self):
        G, layers = build_simple_graph()
        viz = GraphVisualizer(G, layers)
        params = {"Iterations": 1, "Seeds": ["GeneA"]}
        layer_names = {"1": "Genes", "2": "Diseases"}
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "graph.html")
            fig = viz.create_interactive_graph(out, seeds=["GeneA"], params=params, layer_names=layer_names)
            self.assertIsNotNone(fig)


if __name__ == "__main__":
    unittest.main()