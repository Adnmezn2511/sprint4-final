import unittest
import os
import tempfile
import pandas as pd
from app.itRWR.sif_utils import correct_sif_order, filter_sif_file


class TestFilterSifFile(unittest.TestCase):
    """Tests de non-régression pour filter_sif_file."""

    def _write_sif(self, directory, lines):
        path = os.path.join(directory, "ranking.sif")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path

    def test_keeps_valid_edges_both_nodes_in_ranking(self):
        """Les deux nœuds dans ranking_final → ligne conservée."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = self._write_sif(tmp, ["A\tpp\tB", "A\tpp\tC"])
            df = pd.DataFrame({"node": ["A", "B"]})
            filter_sif_file(sif, df)
            with open(sif) as f:
                lines = [l.strip() for l in f if l.strip()]
            self.assertEqual(lines, ["A\tpp\tB"])

    def test_removes_edges_with_unknown_left_node(self):
        """Nœud gauche absent de ranking_final → ligne supprimée."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = self._write_sif(tmp, ["X\tpp\tB"])
            df = pd.DataFrame({"node": ["A", "B"]})
            filter_sif_file(sif, df)
            with open(sif) as f:
                content = f.read().strip()
            self.assertEqual(content, "")

    def test_removes_edges_with_unknown_right_node(self):
        """Nœud droit absent de ranking_final → ligne supprimée."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = self._write_sif(tmp, ["A\tpp\tZ"])
            df = pd.DataFrame({"node": ["A", "B"]})
            filter_sif_file(sif, df)
            with open(sif) as f:
                content = f.read().strip()
            self.assertEqual(content, "")

    def test_empty_sif_no_error(self):
        """Fichier SIF vide → pas d'erreur, fichier reste vide."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = self._write_sif(tmp, [])
            df = pd.DataFrame({"node": ["A"]})
            filter_sif_file(sif, df)
            with open(sif) as f:
                self.assertEqual(f.read().strip(), "")

    def test_malformed_lines_less_than_3_cols_ignored(self):
        """Lignes avec < 3 colonnes ignorées sans lever d'exception."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = self._write_sif(tmp, ["A\tpp\tB", "malformed_line"])
            df = pd.DataFrame({"node": ["A", "B"]})
            filter_sif_file(sif, df)
            with open(sif) as f:
                lines = [l.strip() for l in f if l.strip()]
            self.assertEqual(lines, ["A\tpp\tB"])

    def test_empty_ranking_removes_all(self):
        """ranking_final vide → toutes les lignes supprimées."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = self._write_sif(tmp, ["A\tpp\tB", "C\tpp\tD"])
            df = pd.DataFrame({"node": []})
            filter_sif_file(sif, df)
            with open(sif) as f:
                content = f.read().strip()
            self.assertEqual(content, "")

    def test_multiple_valid_edges_all_kept(self):
        """Plusieurs arêtes valides → toutes conservées."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = self._write_sif(tmp, ["A\tpp\tB", "C\tpp\tD", "A\tpp\tC"])
            df = pd.DataFrame({"node": ["A", "B", "C", "D"]})
            filter_sif_file(sif, df)
            with open(sif) as f:
                lines = [l.strip() for l in f if l.strip()]
            self.assertEqual(len(lines), 3)

    def test_blank_lines_in_sif_ignored(self):
        """Lignes vides dans le SIF → ignorées proprement."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = self._write_sif(tmp, ["A\tpp\tB", "", "C\tpp\tD"])
            df = pd.DataFrame({"node": ["A", "B", "C", "D"]})
            filter_sif_file(sif, df)
            with open(sif) as f:
                lines = [l.strip() for l in f if l.strip()]
            self.assertEqual(len(lines), 2)


class TestCorrectSifOrder(unittest.TestCase):
    """Tests de non-régression pour correct_sif_order."""

    def _create_multiplex_tsv(self, directory, layer_id, nodes):
        """Crée un fichier multiplex_<id>.tsv avec les nœuds donnés."""
        path = os.path.join(directory, f"multiplex_{layer_id}.tsv")
        with open(path, "w") as f:
            f.write("multiplex\tnode\tlayer\tscore\n")
            for n in nodes:
                f.write(f"{layer_id}\t{n}\tlayer{layer_id}\t0.5\n")
        return path

    def test_non_bipartite_relation_unchanged(self):
        """Relation non-bipartite (multiplex/...) → ordre inchangé."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = os.path.join(tmp, "ranking.sif")
            with open(sif, "w") as f:
                f.write("A\tmultiplex/1/genes.tsv\tB\n")
            self._create_multiplex_tsv(tmp, "1", ["A", "B"])
            correct_sif_order(sif, tmp)
            with open(sif) as f:
                result = f.read().strip()
            self.assertEqual(result, "A\tmultiplex/1/genes.tsv\tB")

    def test_bipartite_swaps_when_right_in_layer1(self):
        """Bipartite: nœud droit dans layer1, gauche non → échange."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = os.path.join(tmp, "ranking.sif")
            with open(sif, "w") as f:
                f.write("B\tbipartite/1_2.tsv\tA\n")
            # A est dans layer 1, B dans layer 2
            self._create_multiplex_tsv(tmp, "1", ["A"])
            self._create_multiplex_tsv(tmp, "2", ["B"])
            correct_sif_order(sif, tmp)
            with open(sif) as f:
                result = f.read().strip()
            self.assertEqual(result, "A\tbipartite/1_2.tsv\tB")

    def test_duplicate_lines_removed(self):
        """La même arête dupliquée → une seule occurrence."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = os.path.join(tmp, "ranking.sif")
            with open(sif, "w") as f:
                f.write("A\tmultiplex/1/genes.tsv\tB\n")
                f.write("A\tmultiplex/1/genes.tsv\tB\n")
            self._create_multiplex_tsv(tmp, "1", ["A", "B"])
            correct_sif_order(sif, tmp)
            with open(sif) as f:
                lines = [l.strip() for l in f if l.strip()]
            self.assertEqual(len(lines), 1)

    def test_empty_sif_no_error(self):
        """SIF vide → pas d'erreur, fichier reste vide."""
        with tempfile.TemporaryDirectory() as tmp:
            sif = os.path.join(tmp, "ranking.sif")
            open(sif, "w").close()
            correct_sif_order(sif, tmp)
            with open(sif) as f:
                self.assertEqual(f.read().strip(), "")

    def test_output_file_different_from_input(self):
        """Paramètre output_file → écriture dans un fichier différent."""
        with tempfile.TemporaryDirectory() as tmp:
            sif_in = os.path.join(tmp, "input.sif")
            sif_out = os.path.join(tmp, "output.sif")
            with open(sif_in, "w") as f:
                f.write("A\tmultiplex/1/genes.tsv\tB\n")
            self._create_multiplex_tsv(tmp, "1", ["A", "B"])
            correct_sif_order(sif_in, tmp, output_file=sif_out)
            self.assertTrue(os.path.exists(sif_out))


if __name__ == "__main__":
    unittest.main()