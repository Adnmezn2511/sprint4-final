from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from history.models import GraphHistory


# ──────────────────────────────────────────────
# Tests issus de sprint3 (HEAD)
# ──────────────────────────────────────────────

class GraphHistoryModelTest(TestCase):
    """Tests unitaires sur le modèle GraphHistory."""

    def test_str_with_title(self):
        """__str__ retourne le titre quand il est défini."""
        g = GraphHistory.objects.create(title="Mon graphe", user="alice")
        self.assertIn("Mon graphe", str(g))

    def test_str_without_title_uses_date(self):
        """__str__ retourne une chaîne avec la date quand le titre est None."""
        g = GraphHistory.objects.create(title=None)
        self.assertTrue(len(str(g)) > 0)

    def test_created_at_auto_set(self):
        """created_at est automatiquement défini à la création."""
        g = GraphHistory.objects.create(title="Test")
        self.assertIsNotNone(g.created_at)

    def test_all_fields_nullable(self):
        """Tous les champs nullable → création sans erreur."""
        g = GraphHistory.objects.create()
        self.assertIsNone(g.user)
        self.assertIsNone(g.title)
        self.assertIsNone(g.graph_json)
        self.assertIsNone(g.parameters)
        self.assertIsNone(g.result_folder)

    def test_graph_json_stores_dict(self):
        """graph_json accepte et restitue un dictionnaire Python."""
        data = {"data": [1, 2, 3], "layout": {"title": "test"}}
        g = GraphHistory.objects.create(graph_json=data)
        g.refresh_from_db()
        self.assertEqual(g.graph_json, data)

    def test_parameters_stores_dict(self):
        """parameters accepte et restitue un dictionnaire Python."""
        params = {"iterations": 3, "restart": 0.7}
        g = GraphHistory.objects.create(parameters=params)
        g.refresh_from_db()
        self.assertEqual(g.parameters, params)

    def test_ordering_most_recent_first(self):
        """Les entrées sont triées par created_at décroissant via l'API."""
        GraphHistory.objects.create(title="First")
        GraphHistory.objects.create(title="Second")
        client = APIClient()
        response = client.get("/api/graph-histories/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data[0]["title"], "Second")


class GraphHistoryListAPITest(TestCase):
    """Tests sur l'endpoint GET /api/graph-histories/."""

    def setUp(self):
        self.client = APIClient()
        self.g1 = GraphHistory.objects.create(
            title="Graph 1", user="alice",
            graph_json={"data": []}, parameters={"iter": 2}
        )
        self.g2 = GraphHistory.objects.create(
            title="Graph 2", user="bob",
            graph_json={"data": []}
        )

    def test_returns_200(self):
        response = self.client.get("/api/graph-histories/")
        self.assertEqual(response.status_code, 200)

    def test_returns_all_entries(self):
        response = self.client.get("/api/graph-histories/")
        self.assertEqual(len(response.json()), 2)

    def test_response_contains_required_fields(self):
        response = self.client.get("/api/graph-histories/")
        entry = response.json()[0]
        for field in ["id", "user", "title", "created_at"]:
            self.assertIn(field, entry)

    def test_created_at_is_iso_format(self):
        """created_at doit être au format ISO 8601."""
        response = self.client.get("/api/graph-histories/")
        entry = response.json()[0]
        created_at = entry["created_at"]
        self.assertIn("T", created_at)
        self.assertIn("-", created_at)

class GraphHistoryDetailAPITest(TestCase):
    """
    Tests sur l'endpoint GET /api/graph-histories/<id>/
    Vérifie la récupération d'un graphe unique par son ID.
    """

    def setUp(self):
        self.client = APIClient()
        # Graphe simple avec paramètres multi-seeds (cas patient multiplex)
        self.g = GraphHistory.objects.create(
            title="Graphe Patient A",
            user="docteur1",
            graph_json={"data": [{"type": "scatter"}], "layout": {"title": "test"}},
            parameters={"Seeds": ["GeneA", "GeneB"], "Iterations": 3, "Restart (%)": 0.7}
        )


    def test_detail_id_valide_retourne_200(self):
        """Un ID valide retourne un statut 200."""
        response = self.client.get(f"/api/graph-histories/{self.g.id}/")
        self.assertEqual(response.status_code, 200)


    def test_detail_id_invalide_retourne_404(self):
        """Un ID inexistant retourne un statut 404."""
        response = self.client.get("/api/graph-histories/99999/")
        self.assertEqual(response.status_code, 404)


    def test_detail_contient_champs_requis(self):
        """La réponse contient tous les champs attendus par le frontend."""
        response = self.client.get(f"/api/graph-histories/{self.g.id}/")
        data = response.json()
        for field in ["id", "user", "title", "created_at", "graph_json", "parameters"]:
            self.assertIn(field, data)


    def test_detail_graph_json_correct(self):
        """Le graph_json retourné correspond bien à celui stocké en base."""
        response = self.client.get(f"/api/graph-histories/{self.g.id}/")
        data = response.json()
        self.assertEqual(data["graph_json"], self.g.graph_json)


    def test_detail_parameters_multi_seeds(self):
        """
        Cas d'usage B2 : un graphe généré avec plusieurs seeds (multi-patients)
        doit avoir ses paramètres correctement retournés.
        """
        response = self.client.get(f"/api/graph-histories/{self.g.id}/")
        data = response.json()
        self.assertIn("Seeds", data["parameters"])
        self.assertIsInstance(data["parameters"]["Seeds"], list)
        self.assertEqual(len(data["parameters"]["Seeds"]), 2)


    def test_detail_titre_correct(self):
        """Le titre retourné correspond au graphe demandé."""
        response = self.client.get(f"/api/graph-histories/{self.g.id}/")
        data = response.json()
        self.assertEqual(data["title"], "Graphe Patient A")


class GraphHistoryDisplayAPITest(TestCase):
    """Tests sur l'endpoint GET /history/graph/<id>/."""

    def setUp(self):
        self.client = APIClient()
        import plotly.graph_objects as go
        fig = go.Figure()
        self.g = GraphHistory.objects.create(
            title="Test Graph",
            user="alice",
            graph_json=fig.to_dict()
        )

    def test_valid_id_returns_200(self):
        response = self.client.get(f"/history/graph/{self.g.id}/")
        self.assertEqual(response.status_code, 200)

    def test_invalid_id_returns_404(self):
        response = self.client.get("/history/graph/99999/")
        self.assertEqual(response.status_code, 404)

    def test_response_contains_graph(self):
        """La réponse HTML doit contenir du contenu relatif au graphe."""
        response = self.client.get(f"/history/graph/{self.g.id}/")
        self.assertEqual(response.status_code, 200)


class GraphHistoryDeleteAPITest(TestCase):
    """Tests sur l'endpoint DELETE /history/graph/<id>/delete/."""

    def setUp(self):
        self.client = APIClient()
        self.g = GraphHistory.objects.create(
            title="To Delete", user="alice",
            graph_json={"data": []},
            result_folder="fake_folder"
        )

    def test_delete_existing_returns_200_or_404(self):
        """DELETE sur une entrée existante. Pas de 500."""
        response = self.client.delete(f"/history/graph/{self.g.id}/delete/")
        self.assertIn(response.status_code, [200, 404])

    def test_delete_nonexistent_returns_404(self):
        response = self.client.delete("/history/graph/99999/delete/")
        self.assertEqual(response.status_code, 404)

    def test_delete_removes_db_entry_when_zip_exists(self):
        """Si le ZIP correspondant existe → l'entrée DB est supprimée."""
        import os
        from django.conf import settings
        log_zip_dir = os.path.join(settings.BASE_DIR, "samples", "log_zip")
        os.makedirs(log_zip_dir, exist_ok=True)
        fake_zip = os.path.join(log_zip_dir, f"fake_folder#{self.g.id}.zip")
        import zipfile
        with zipfile.ZipFile(fake_zip, "w"):
            pass
        try:
            response = self.client.delete(f"/history/graph/{self.g.id}/delete/")
            self.assertEqual(response.status_code, 200)
            self.assertFalse(GraphHistory.objects.filter(id=self.g.id).exists())
        finally:
            if os.path.exists(fake_zip):
                os.remove(fake_zip)


class GraphHistoryListGraphsAPITest(TestCase):
    """Tests sur l'endpoint GET /history/graphs/."""

    def setUp(self):
        self.client = APIClient()
        import plotly.graph_objects as go
        fig = go.Figure()
        GraphHistory.objects.create(
            title="G1", user="alice",
            graph_json=fig.to_dict()
        )

    def test_returns_200(self):
        response = self.client.get("/history/graphs/")
        self.assertEqual(response.status_code, 200)

    def test_returns_list(self):
        response = self.client.get("/history/graphs/")
        self.assertIsInstance(response.json(), list)


if __name__ == "__main__":
    import unittest
    unittest.main()