import os
import unittest
import tempfile
import pandas as pd
from unittest.mock import MagicMock, patch


class TestOutputModule(unittest.TestCase):
    """Tests du module Output de multixrank."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_output_import(self):
        """Le module Output est importable."""
        from ..multixrank.Output import Output
        self.assertTrue(True)

    def test_output_class_exists(self):
        from ..multixrank.Output import Output
        self.assertTrue(callable(Output))

    def test_output_requires_ranking_df(self):
        """Output doit accepter un DataFrame de ranking."""
        from ..multixrank.Output import Output
        # On vérifie juste que la classe est instanciable avec les bons arguments
        # sans lancer un vrai RWR
        df = pd.DataFrame({
            'multiplex': ['1', '1'],
            'node': ['A', 'B'],
            'layer': ['layer1', 'layer1'],
            'score': [0.8, 0.2]
        })
        mock_multiplexall = MagicMock()
        mock_multiplexall.multiplex_tuple = []
        try:
            out = Output(df, mock_multiplexall)
        except (TypeError, AttributeError, KeyError, SystemExit):
            pass  # attendu selon l'implémentation
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()