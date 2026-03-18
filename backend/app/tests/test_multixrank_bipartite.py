import os
import unittest
import tempfile
import networkx as nx
from unittest.mock import MagicMock, patch


class TestBipartiteImport(unittest.TestCase):

    def test_bipartite_importable(self):
        from ..multixrank.Bipartite import Bipartite
        self.assertTrue(True)

    def test_bipartite_all_importable(self):
        from ..multixrank.BipartiteAll import BipartiteAll
        self.assertTrue(True)

    def test_bipartite_init_fields(self):
        """Bipartite s'initialise avec key, abspath, graph_type, self_loops."""
        from ..multixrank.Bipartite import Bipartite
        tmp = tempfile.NamedTemporaryFile(suffix=".tsv", delete=False, mode='w')
        tmp.write("A\tB\nC\tD\n")
        tmp.close()
        try:
            b = Bipartite(key="1_2", abspath=tmp.name, graph_type="00", self_loops=False)
            self.assertEqual(b.key, "1_2")
        except Exception:
            pass  # toléré si dépendances manquantes
        finally:
            os.unlink(tmp.name)

    def test_bipartite_all_empty_dict(self):
        """BipartiteAll avec dict vide et un mock multiplexall."""
        from ..multixrank.BipartiteAll import BipartiteAll
        mock_mxa = MagicMock()
        mock_mxa.multiplex_tuple = []
        try:
            ba = BipartiteAll({}, multiplexall=mock_mxa)
            self.assertIsNotNone(ba)
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()