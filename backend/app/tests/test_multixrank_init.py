import os
import unittest
import tempfile
import shutil
import yaml


class TestMultixrankInit(unittest.TestCase):
    """Tests d'intégration légers pour la classe Multixrank."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _create_minimal_network(self):
        """Crée un réseau multiplex minimal pour les tests."""
        multiplex_dir = os.path.join(self.tmp, "multiplex", "1")
        os.makedirs(multiplex_dir, exist_ok=True)
        layer_path = os.path.join(multiplex_dir, "layer1.tsv")
        with open(layer_path, "w") as f:
            f.write("GeneA\tGeneB\nGeneB\tGeneC\nGeneC\tGeneA\n")

        seeds_path = os.path.join(self.tmp, "seeds.txt")
        with open(seeds_path, "w") as f:
            f.write("GeneA\n")

        config = {
            "multiplex": {
                "1": {
                    "layers": ["multiplex/1/layer1.tsv"]
                }
            },
            "seed": seeds_path,
            "r": 0.7
        }
        config_path = os.path.join(self.tmp, "config.yml")
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        return config_path

    def test_multixrank_import(self):
        from ..multixrank import Multixrank
        self.assertTrue(True)

    def test_multixrank_example_class(self):
        from ..multixrank import Example
        e = Example()
        self.assertIsNotNone(e)

    def test_multixrank_example_has_airport_path(self):
        from ..multixrank import Example
        e = Example()
        self.assertTrue(hasattr(e, 'airport_input_path'))

    def test_multixrank_init_invalid_config(self):
        """Config inexistant → SystemExit ou exception."""
        from ..multixrank import Multixrank
        with self.assertRaises((SystemExit, FileNotFoundError, Exception)):
            Multixrank(config="/nonexistent/config.yml", wdir=self.tmp)

    def test_multixrank_version(self):
        from ..multixrank import __version__
        self.assertIsInstance(__version__, str)


if __name__ == "__main__":
    unittest.main()