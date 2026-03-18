import os
import tempfile
import unittest
from app.itRWR.file_utils import write_config_file, read_seeds, write_seeds


class TestWriteConfigFileNominal(unittest.TestCase):
    """Tests du cas nominal de write_config_file (cas commenté décommenté et adapté)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.tmp.name, "config.yml")
        self.out_folder = os.path.join(self.tmp.name, "output")
        os.mkdir(self.out_folder)
        with open(self.config_file, "w") as f:
            f.write("seed: /old/path/seeds.txt\neta: 0.5\nr: 0.7\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_output_config_file_created(self):
        """Le fichier config.yml est créé dans out_folder."""
        write_config_file(self.config_file, self.out_folder)
        output_config = os.path.join(self.out_folder, "config.yml")
        self.assertTrue(os.path.exists(output_config))

    def test_first_line_updated_to_new_seed_path(self):
        """La première ligne (seed) pointe vers out_folder/seeds.txt."""
        write_config_file(self.config_file, self.out_folder)
        output_config = os.path.join(self.out_folder, "config.yml")
        with open(output_config) as f:
            first_line = f.readline().strip()
        expected_path = os.path.join(self.out_folder, "seeds.txt")
        self.assertIn(expected_path, first_line)

    def test_other_lines_unchanged(self):
        """Les autres lignes (eta, r) ne sont pas modifiées."""
        write_config_file(self.config_file, self.out_folder)
        output_config = os.path.join(self.out_folder, "config.yml")
        with open(output_config) as f:
            content = f.read()
        self.assertIn("eta: 0.5", content)
        self.assertIn("r: 0.7", content)

    def test_original_config_not_modified(self):
        """Le fichier config original n'est pas modifié."""
        write_config_file(self.config_file, self.out_folder)
        with open(self.config_file) as f:
            content = f.read()
        self.assertIn("/old/path/seeds.txt", content)

    def test_config_with_single_line_no_crash(self):
        """Config avec une seule ligne (seed) → pas d'erreur."""
        with open(self.config_file, "w") as f:
            f.write("seed: /old/path/seeds.txt\n")
        write_config_file(self.config_file, self.out_folder)
        output_config = os.path.join(self.out_folder, "config.yml")
        self.assertTrue(os.path.exists(output_config))


class TestWriteSeeds(unittest.TestCase):
    """Tests pour write_seeds (non testé jusqu'ici)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_file(self):
        path = os.path.join(self.tmp.name, "seeds.txt")
        write_seeds({"GeneA", "GeneB"}, path)
        self.assertTrue(os.path.exists(path))

    def test_written_seeds_readable_by_read_seeds(self):
        """write_seeds puis read_seeds → retourne le même ensemble."""
        path = os.path.join(self.tmp.name, "seeds.txt")
        seeds = {"GeneA", "GeneB", "GeneC"}
        write_seeds(seeds, path)
        result = read_seeds(path)
        self.assertEqual(result, seeds)

    def test_single_seed(self):
        path = os.path.join(self.tmp.name, "seeds.txt")
        write_seeds({"OnlySeed"}, path)
        result = read_seeds(path)
        self.assertEqual(result, {"OnlySeed"})

    def test_empty_set_creates_empty_file(self):
        path = os.path.join(self.tmp.name, "seeds.txt")
        write_seeds(set(), path)
        self.assertTrue(os.path.exists(path))
        result = read_seeds(path)
        # Fichier vide → set vide (ou set avec chaîne vide selon implémentation)
        self.assertIsInstance(result, set)

    def test_overwrites_existing_file(self):
        """Appel successif → le fichier est écrasé, pas appendé."""
        path = os.path.join(self.tmp.name, "seeds.txt")
        write_seeds({"OldSeed"}, path)
        write_seeds({"NewSeed"}, path)
        result = read_seeds(path)
        self.assertNotIn("OldSeed", result)
        self.assertIn("NewSeed", result)

    def test_seeds_one_per_line(self):
        """Chaque graine est sur une ligne distincte."""
        path = os.path.join(self.tmp.name, "seeds.txt")
        seeds = {"A", "B", "C"}
        write_seeds(seeds, path)
        with open(path) as f:
            lines = [l.strip() for l in f if l.strip()]
        self.assertEqual(len(lines), 3)


class TestReadSeeds(unittest.TestCase):
    """Tests complémentaires pour read_seeds."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_reads_multiple_seeds(self):
        path = os.path.join(self.tmp.name, "seeds.txt")
        with open(path, "w") as f:
            f.write("GeneA\nGeneB\nGeneC\n")
        result = read_seeds(path)
        self.assertEqual(result, {"GeneA", "GeneB", "GeneC"})

    def test_strips_newlines(self):
        path = os.path.join(self.tmp.name, "seeds.txt")
        with open(path, "w") as f:
            f.write("GeneA\n")
        result = read_seeds(path)
        self.assertIn("GeneA", result)
        # Vérifie qu'il n'y a pas de \n traînant
        for seed in result:
            self.assertNotIn("\n", seed)

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            read_seeds("/non/existent/path/seeds.txt")


if __name__ == "__main__":
    unittest.main()