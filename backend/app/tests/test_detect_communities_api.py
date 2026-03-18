import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
import networkx as nx


# ── helpers ──────────────────────────────────────────────────────────────────

def _write_sif(directory, lines):
    path = os.path.join(directory, "ranking.sif")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


factory = APIRequestFactory()


# ── Import de la vue (chemin réel dans le projet) ────────────────────────────
from app.views import detectCommunities


class TestDetectCommunitiesAPI(unittest.TestCase):
    """Tests API pour l'endpoint POST graph/communities/."""

    # ── cas nominaux ─────────────────────────────────────────────────────────

    @patch("app.views.CommunityDetector")
    @patch("app.views.MultiplexGraph")
    def test_returns_200_with_valid_params(self, mock_mg_cls, mock_cd_cls):
        """Paramètres valides → 200 avec structure attendue."""
        mock_G = MagicMock(spec=nx.Graph)
        mock_G.number_of_nodes.return_value = 4
        mock_mg = MagicMock()
        mock_mg.get_graph.return_value = (mock_G, ["1"])
        mock_mg_cls.return_value = mock_mg

        mock_cd = MagicMock()
        mock_cd.detect.return_value = [["GeneA", "GeneB"], ["GeneC"]]
        mock_cd_cls.return_value = mock_cd
        mock_cd_cls.SUPPORTED_ALGORITHMS = ("louvain", "greedy", "connected", "scc")
        mock_cd_cls.communities_to_dict.return_value = {
            "nb_communities": 2,
            "communities": [
                {"id": 0, "size": 2, "nodes": ["GeneA", "GeneB"]},
                {"id": 1, "size": 1, "nodes": ["GeneC"]},
            ],
        }

        with tempfile.NamedTemporaryFile(suffix=".sif", delete=False) as f:
            f.write(b"GeneA\tmultiplex/1/genes.tsv\tGeneB\n")
            sif_path = f.name

        try:
            request = factory.post(
                "/graph/communities/",
                {"sif_file": sif_path, "algorithm": "louvain"},
                format="json",
            )
            response = detectCommunities(request)
            self.assertEqual(response.status_code, 200)
            self.assertIn("nb_communities", response.data)
            self.assertIn("algorithm", response.data)
        finally:
            os.unlink(sif_path)

    @patch("app.views.CommunityDetector")
    @patch("app.views.MultiplexGraph")
    def test_all_algorithms_accepted(self, mock_mg_cls, mock_cd_cls):
        """Chaque algorithme supporté doit être accepté (pas de 400)."""
        mock_G = MagicMock(spec=nx.Graph)
        mock_G.number_of_nodes.return_value = 2
        mock_mg = MagicMock()
        mock_mg.get_graph.return_value = (mock_G, ["1"])
        mock_mg_cls.return_value = mock_mg
        mock_cd = MagicMock()
        mock_cd.detect.return_value = [["A"]]
        mock_cd_cls.return_value = mock_cd
        mock_cd_cls.SUPPORTED_ALGORITHMS = ("louvain", "greedy", "connected", "scc")
        mock_cd_cls.communities_to_dict.return_value = {"nb_communities": 1, "communities": []}

        with tempfile.NamedTemporaryFile(suffix=".sif", delete=False) as f:
            f.write(b"A\tmultiplex/1/g.tsv\tB\n")
            sif_path = f.name

        try:
            for algo in ("louvain", "greedy", "connected", "scc"):
                request = factory.post(
                    "/graph/communities/",
                    {"sif_file": sif_path, "algorithm": algo},
                    format="json",
                )
                response = detectCommunities(request)
                self.assertNotEqual(response.status_code, 400, msg=f"Algo '{algo}' rejeté à tort")
        finally:
            os.unlink(sif_path)

    # ── cas d'erreur ─────────────────────────────────────────────────────────

    def test_missing_sif_file_returns_400(self):
        """Pas de sif_file → 400."""
        request = factory.post("/graph/communities/", {}, format="json")
        response = detectCommunities(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_nonexistent_sif_file_returns_400(self):
        """sif_file inexistant → 400."""
        request = factory.post(
            "/graph/communities/",
            {"sif_file": "/nonexistent/path.sif"},
            format="json",
        )
        response = detectCommunities(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_unsupported_algorithm_returns_400(self):
        """Algorithme inconnu → 400 avec liste des algorithmes supportés."""
        with tempfile.NamedTemporaryFile(suffix=".sif", delete=False) as f:
            f.write(b"A\tmultiplex/1/g.tsv\tB\n")
            sif_path = f.name
        try:
            request = factory.post(
                "/graph/communities/",
                {"sif_file": sif_path, "algorithm": "unknown_algo"},
                format="json",
            )
            response = detectCommunities(request)
            self.assertEqual(response.status_code, 400)
            self.assertIn("supported", response.data)
        finally:
            os.unlink(sif_path)

    @patch("app.views.CommunityDetector")
    @patch("app.views.MultiplexGraph")
    def test_runtime_error_returns_500(self, mock_mg_cls, mock_cd_cls):
        """RuntimeError interne → 500."""
        mock_G = MagicMock(spec=nx.Graph)
        mock_G.number_of_nodes.return_value = 2
        mock_mg = MagicMock()
        mock_mg.get_graph.return_value = (mock_G, ["1"])
        mock_mg_cls.return_value = mock_mg
        mock_cd = MagicMock()
        mock_cd.detect.side_effect = RuntimeError("algo a planté")
        mock_cd_cls.return_value = mock_cd
        mock_cd_cls.SUPPORTED_ALGORITHMS = ("louvain", "greedy", "connected", "scc")

        with tempfile.NamedTemporaryFile(suffix=".sif", delete=False) as f:
            f.write(b"A\tmultiplex/1/g.tsv\tB\n")
            sif_path = f.name
        try:
            request = factory.post(
                "/graph/communities/",
                {"sif_file": sif_path, "algorithm": "louvain"},
                format="json",
            )
            response = detectCommunities(request)
            self.assertEqual(response.status_code, 500)
        finally:
            os.unlink(sif_path)

    @patch("app.views.CommunityDetector")
    @patch("app.views.MultiplexGraph")
    def test_value_error_returns_400(self, mock_mg_cls, mock_cd_cls):
        """ValueError (ex : graphe vide) → 400."""
        mock_mg = MagicMock()
        mock_mg.get_graph.return_value = (MagicMock(spec=nx.Graph), [])
        mock_mg_cls.return_value = mock_mg
        mock_cd_cls.SUPPORTED_ALGORITHMS = ("louvain", "greedy", "connected", "scc")
        mock_cd_cls.side_effect = ValueError("Le graphe fourni est vide ou None.")

        with tempfile.NamedTemporaryFile(suffix=".sif", delete=False) as f:
            f.write(b"")
            sif_path = f.name
        try:
            request = factory.post(
                "/graph/communities/",
                {"sif_file": sif_path, "algorithm": "louvain"},
                format="json",
            )
            response = detectCommunities(request)
            self.assertEqual(response.status_code, 400)
        finally:
            os.unlink(sif_path)

    def test_nonexistent_ranking_file_returns_400(self):
        """ranking_file fourni mais inexistant → 400."""
        with tempfile.NamedTemporaryFile(suffix=".sif", delete=False) as f:
            f.write(b"A\tmultiplex/1/g.tsv\tB\n")
            sif_path = f.name
        try:
            request = factory.post(
                "/graph/communities/",
                {"sif_file": sif_path, "ranking_file": "/nonexistent/ranking.csv"},
                format="json",
            )
            response = detectCommunities(request)
            self.assertEqual(response.status_code, 400)
        finally:
            os.unlink(sif_path)


if __name__ == "__main__":
    unittest.main()